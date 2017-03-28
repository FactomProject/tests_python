import unittest
import os, binascii

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack
from nose.plugins.attrib import attr

@attr(fast=True)
class FactomCliTransactionTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    path = ''
    ACK_WAIT_TIME = 20

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet2, '1000')
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)

    def tearDown(self):
        if os.path.exists('output_file'):
            os.remove('output_file')


    def test_make_entries(self):
        # create chain
        name_1 = create_random_string(5)
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(1))
            path = fout.name

        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['CommitTxID']
        chain_id = chain_dict['ChainID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)

        # make entry return tx id
        ext_id = create_random_string(5)
        tx_id = self.factom_chain_object.add_entry_to_chain_return_tx_id(self.entry_creds_wallet2, path,
                                                                                            chain_id, ext_id)
        # any error message will contain a capital letter
        self.assertTrue(not any(map(str.isupper, tx_id)), "tx_id not returned")

        # make entry by chain external id return chain id
        chain_ext_id = name_1
        chain_id = self.factom_chain_object.add_entry_to_chain_by_ext_id_return_chain_id(self.entry_creds_wallet2, path,
                                                                           chain_ext_id, ext_id)

        # force entry by chain external id
        chain_ext_id = name_1
        ext_id = create_random_string(5)
        text = self.factom_chain_object.force_add_entry_to_chain_by_ext_id(self.entry_creds_wallet2, path,
                                                                           chain_ext_id, ext_id)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['CommitTxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        self.assertTrue("TransactionACK" in self.factom_cli_create.request_transaction_acknowledgement(tx_id))

        # make entry by hex external id
        hex_ext_id = binascii.hexlify(chain_ext_id)
        ext_id = create_random_string(5)
        text = self.factom_chain_object.add_entry_to_chain_by_hex_ext_id(self.entry_creds_wallet2, path,
                                                                         hex_ext_id, ext_id)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['CommitTxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        self.assertTrue("TransactionACK" in self.factom_cli_create.request_transaction_acknowledgement(tx_id))

    def test_quiet_make_entries(self):
        '''
        This test will only be effective the 1st time it is run as afterwards the chain will already exist.
        This structure is necessary because there is no other way to determine the success of the chain creation without a tx_id.
         '''
        # create known chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['known_chain_3_name']
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1)
        chain_id = self.data['known_chain_3_chain_id']

        # quiet entry by hex external id
        chain_ext_id = name_1
        hex_ext_id = binascii.hexlify(chain_ext_id)
        ext_id = self.data['known_chain_3_ext_id_1']
        self.factom_chain_object.quiet_add_entry_to_chain_by_hex_ext_id(self.entry_creds_wallet2, path, hex_ext_id, ext_id)
        self.assertTrue(
            "Entry not found" not in self.factom_chain_object.get_entryhash(self.data['known_chain_3_chain_hash']),
            "Entry not created")
        self.assertTrue(
        "EntryHash: " + self.data['known_chain_3_entry_hash_1'] in self.factom_chain_object.get_allentries(chain_id), "Entry hash incorrect")

        # make entry return entry hash
        ext_id = self.data['known_chain_3_ext_id_2']
        self.factom_chain_object.quiet_add_entry_to_chain_by_hex_ext_id(self.entry_creds_wallet2, path, hex_ext_id, ext_id)
        self.factom_chain_object.add_entry_to_chain_return_entry_hash(self.entry_creds_wallet2, path,
                                                                      chain_id, ext_id)
        self.assertTrue(
        "EntryHash: " + self.data['known_chain_3_entry_hash_1'] in self.factom_chain_object.get_allentries(chain_id))

    def test_verify_entry_costs(self):
        # create chain
        ONE_K_MINUS_8 = 1016
        MAX_ENTRY_SIZE_MINUS_7 = 10233
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        firstentry_ext_id = name_1

        i = ONE_K_MINUS_8
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(i))
            self.path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet1, self.path, name_1, name_2)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        chain_id = chain_dict['ChainID']
        tx_id = chain_dict['CommitTxID']
        wait_for_ack(tx_id,self.ACK_WAIT_TIME)

        balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)

        # make entries
        while i < MAX_ENTRY_SIZE_MINUS_7:
            # write largest entry for fee amount
            name_1 = create_random_string(2)
            name_2 = create_random_string(2)
            text = self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet1, self.path, chain_id, name_1,
                                                               name_2)
            chain_dict = self.factom_chain_object.parse_chain_data(text)
            tx_id = chain_dict['CommitTxID']
            wait_for_ack(tx_id, self.ACK_WAIT_TIME)
            balance_last = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
            self.assertEqual(int(balance_1st), int(balance_last) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            # make smallest entry for fee amount
            i += 1
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1))
            if i == MAX_ENTRY_SIZE_MINUS_7:
                break
            name_1 = binascii.b2a_hex(os.urandom(2))
            name_2 = binascii.b2a_hex(os.urandom(2))
            text = self.factom_chain_object.add_entry_to_chain_with_hex_ext(self.entry_creds_wallet1, self.path, chain_id, name_1, name_2)
            chain_dict = self.factom_chain_object.parse_chain_data(text)
            tx_id = chain_dict['CommitTxID']
            wait_for_ack(tx_id,self.ACK_WAIT_TIME)
            balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
            self.assertEqual(int(balance_last), int(balance_1st) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            i += 1023
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1023))

        # make too large entry
        name_1 = create_random_string(2)
        name_2 = create_random_string(2)

        self.assertTrue("Entry cannot be larger than 10KB" in self.factom_chain_object.add_entry_to_chain(self.entry_creds_wallet1, self.path, chain_id, name_1, name_2))

        # validate get firstentry command
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry(chain_id))

        # validate get firstentry_with_entryhash command
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry_return_entryhash(chain_id))

        # validate get allentries command
        self.assertTrue("Entry [0]" in self.factom_chain_object.get_allentries(chain_id))


    def test_compose_entry(self):
        # create chain
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)

        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            self.path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet1, self.path, name_1, name_2)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        chain_id = chain_dict['ChainID']

        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        text = self.factom_chain_object.compose_entry_from_binary_file(self.entry_creds_wallet1, self.path, chain_id,
                                                                       name_1, name_2)
        self.assertTrue("commit-entry" in text)
        self.assertTrue("reveal-entry" in text)

