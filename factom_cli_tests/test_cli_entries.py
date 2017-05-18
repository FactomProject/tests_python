import unittest
import os, binascii
from flaky import flaky

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack
from nose.plugins.attrib import attr

@flaky(max_runs=3, min_passes=1)
@attr(fast=True)
class FactomCliTransactionTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    path = ''

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet100 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet100, '100')
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']

    def tearDown(self):
        if self.path:
            os.remove(self.path)

    def test_make_entry_return_entry_hash(self):
       # make chain
        self.entry_creds_wallet100 = self.factom_cli_create.create_entry_credit_address()
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet100, '100')
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, path, names_list)

        # make entry
        with open('output_file', 'a') as fout:
            fout.write(os.urandom(1))
            self.path = fout.name
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-E']
        entry_hash = self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet100, self.path, names_list,
                                                                     flag_list=factom_flags_list)
        self.assertTrue("Entry not found" not in self.factom_chain_object.get_entryhash(entry_hash),
                    "Entry not revealed")

    def test_verify_entry_costs(self):
        # create chain
        ONE_K_MINUS_8 = 1016
        '''entry cost = 1 ec per 1024 bytes
        There are 4 bytes overhead and we are using 2 external ids of 2 bytes each
        1024 - 4(overhead) - 4(2x2 external ids) = 1016'''

        MAX_ENTRY_SIZE_MINUS_7 = 10233
        '''largest allowable entry is 10K = 10240 bytes
        smallest too large entry = 10241 bytes
        10241 - 4(overhead) - 4(2x2 external ids) = 10233'''

        chain_name_1 = create_random_string(5)
        chain_name_2 = create_random_string(5)
        names_list = ['-n', chain_name_1, '-n', chain_name_2]
        firstentry_ext_id = chain_name_1

        i = ONE_K_MINUS_8
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(i))
            self.path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, self.path, names_list)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        chain_id = chain_dict['ChainID']
        tx_id = chain_dict['CommitTxID']
        wait_for_ack(tx_id)
        balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet100)

        # write entries
        while i < MAX_ENTRY_SIZE_MINUS_7:
            # write largest entry for fee amount
            name_1 = create_random_string(2)
            name_2 = create_random_string(2)
            names_list = ['-n', chain_name_1, '-n', chain_name_2, '-e', name_1, '-e', name_2]
            text_raw = self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet100,
                                                                   self.path, names_list)
            tx_id = self.factom_chain_object.parse_entry_data(text_raw)['CommitTxID']
            wait_for_ack(tx_id)
            balance_last = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet100)
            self.assertEqual(int(balance_1st), int(balance_last) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            # write smallest entry for fee amount
            i += 1
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1))
            if i == MAX_ENTRY_SIZE_MINUS_7:
                break
            name_1 = binascii.b2a_hex(os.urandom(2))
            name_2 = binascii.b2a_hex(os.urandom(2))
            names_list = ['-c', chain_id, '-x', name_1, '-x', name_2]
            text_raw = self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet100,
                                                                   self.path, names_list)
            tx_id = self.factom_chain_object.parse_entry_data(text_raw)['CommitTxID']
            wait_for_ack(tx_id)
            balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet100)
            self.assertEqual(int(balance_last), int(balance_1st) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            i += 1023
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1023))

        # write too large entry
        name_1 = create_random_string(2)
        name_2 = create_random_string(2)
        names_list = ['-c', chain_id, '-e', name_1, '-e', name_2]

        self.assertTrue("Entry cannot be larger than 10KB" in self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet100, self.path, names_list))

        # validate get firstentry command
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry(chain_id))

        # validate get firstentry_return_entry_hash
        factom_flags_list = ['-E']
        entry_hash = self.factom_chain_object.get_firstentry(chain_id, flag_list=factom_flags_list)
        self.assertTrue(entry_hash and "Entry [0]" in self.factom_chain_object.get_allentries(chain_id))

    def test_force_make_entry(self):
        # make chain
        self.entry_creds_wallet100 = self.factom_cli_create.create_entry_credit_address()
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet100, '100')
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        names_list = ['-h', name_1, '-h', name_2]
        self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, path, names_list)

        # make entry
        with open('output_file', 'a') as fout:
            fout.write(os.urandom(1))
            self.path = fout.name
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-f', '-T']
        tx_id = self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet100,
                                                               self.path, names_list, flag_list=factom_flags_list)
        wait_for_ack(tx_id)
        self.assertTrue("TransactionACK" in self.factom_cli_create.request_transaction_acknowledgement(tx_id),
                        "Forced entry was not revealed")

    def test_quiet_make_entry(self):
        ''' This test is only reliable on the 1st run on a given database.
          Because of the -q flag, no transaction id is available, so the only way to locate the created entry is by
          using a fixed entry in a fixed chain id which yields a known entry hash. However once this entry is created
          in a database, it will still be there even if subsequent runs fail.'''

        # make chain
        self.entry_creds_wallet100 = self.factom_cli_create.create_entry_credit_address()
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet100, '100')
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['2nd_external_id1']
        name_2 = self.data['2nd_external_id2']
        names_list = ['-n', name_1, '-n', name_2]
        self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, path, names_list)

        # make entry
        with open('output_file', 'a') as fout:
            fout.write('1')
            self.path = fout.name
        name_1 = self.data['3rd_over_2nd_external_id1']
        name_2 = self.data['3rd_over_2nd_external_id2']
        names_list = names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-q']
        self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet100, self.path, names_list, flag_list=factom_flags_list), self.data['3rd_over_2nd_chain_id']
        self.assertTrue("Entry not found" not in self.factom_chain_object.get_entryhash(self.data[
                                                                                            '3rd_over_2nd_entry_hash']))

    def test_compose_entry(self):
        # make chain
            name_1 = create_random_string(5)
            name_2 = create_random_string(5)
            names_list = ['-n', name_1, '-n', name_2]
            with open('output_file', 'wb') as fout:
                fout.write(os.urandom(10))
                self.path = fout.name
            text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, self.path, names_list)
            chain_dict = self.factom_chain_object.parse_chain_data(text)
            chain_id = chain_dict['ChainID']

            # compose entry
            name_1 = create_random_string(5)
            name_2 = create_random_string(5)
            text = self.factom_chain_object.compose_entry_from_binary_file(self.entry_creds_wallet100, self.path, chain_id,
                                                                           name_1, name_2)
            self.assertTrue("message" and "entry" in text)