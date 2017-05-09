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

    def test_file_list(self):
        os.listdir("/home/factom/go/")

    def test_verify_entry_costs(self):
        # create chain
        ONE_K_MINUS_8 = 1016
        MAX_ENTRY_SIZE_MINUS_7 = 10233
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        firstentry_ext_id = name_1

        i = ONE_K_MINUS_8
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(i))
            self.path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, self.path, names_list)
        # print 'text', text
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        chain_id = chain_dict['ChainID']
        tx_id = chain_dict['CommitTxID']
        wait_for_ack(tx_id,20)

        balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet100)

        # write entries
        while i < MAX_ENTRY_SIZE_MINUS_7:
            # write largest entry for fee amount
            name_1 = create_random_string(2)
            name_2 = create_random_string(2)
            names_list = ['-e', name_1, '-e', name_2]
            text_raw = self.factom_chain_object.add_entries_to_chain(self.entry_creds_wallet100,
                                                                     self.path, chain_id, names_list)
            tx_id = self.factom_chain_object.parse_entry_data(text_raw)['CommitTxID']
            wait_for_ack(tx_id, 20)
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
            names_list = ['-x', name_1, '-x', name_2]
            text_raw = self.factom_chain_object.add_entries_to_chain(self.entry_creds_wallet100,
                                                                     self.path, chain_id, names_list)
            tx_id = self.factom_chain_object.parse_entry_data(text_raw)['CommitTxID']
            wait_for_ack(tx_id, 20)
            balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet100)
            self.assertEqual(int(balance_last), int(balance_1st) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            i += 1023
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1023))

        # write too large entry
        name_1 = create_random_string(2)
        name_2 = create_random_string(2)
        names_list = ['-e', name_1, '-e', name_2]

        self.assertTrue("Entry cannot be larger than 10KB" in self.factom_chain_object.add_entries_to_chain(self.entry_creds_wallet100, self.path, chain_id, names_list))

        # validate get firstentry command
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry(chain_id))

        # validate get firstentry_with_entryhash command
        factom_flags_list = ['-E']
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry_with_entryhash(chain_id))

        # validate get allentries command
        self.assertTrue("Entry [0]" in self.factom_chain_object.get_allentries(chain_id))


    def test_compose_entry(self):
        # create chain
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]

        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            self.path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet100, self.path, names_list)
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        chain_id = chain_dict['ChainID']

        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        text = self.factom_chain_object.compose_entry_from_binary_file(self.entry_creds_wallet100, self.path, chain_id,
                                                                       name_1, name_2)
        self.assertTrue("commit-entry" in text, text)
        self.assertTrue("reveal-entry" in text, text)
