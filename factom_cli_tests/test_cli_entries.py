import unittest
import os, binascii

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json
from helpers.factom_cli_methods import wait_for_ack
from nose.plugins.attrib import attr

@attr(fast=True)
class FactomCliTransactionTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])

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
            path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet1, path, name_1, name_2)
        chain_id = text.split('\n')[1].split(' ')[1]
        tx_id = text.split('\n')[0].split(' ')[1]
        wait_for_ack(self, tx_id,20)

        balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)

        # write entries
        while i < MAX_ENTRY_SIZE_MINUS_7:
            # write largest entry for fee amount
            name_1 = create_random_string(2)
            name_2 = create_random_string(2)
            tx_id = self.factom_chain_object.add_entries_to_chain_and_receive_tx_id(self.entry_creds_wallet1,
                                                                                          path, chain_id, name_1,
                                                                                          name_2)
            wait_for_ack(self, tx_id, 20)
            balance_last = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
            self.assertEqual(int(balance_1st), int(balance_last) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            # write smallest entry for fee amount
            i += 1
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1))
            if i == MAX_ENTRY_SIZE_MINUS_7:
                break
            name_1 = binascii.b2a_hex(os.urandom(2))
            name_2 = binascii.b2a_hex(os.urandom(2))
            tx_id = self.factom_chain_object.add_entries_to_chain_with_hex_ext_and_receive_tx_id(self.entry_creds_wallet1, path, chain_id, name_1, name_2)
            wait_for_ack(self, tx_id,20)
            balance_1st = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
            self.assertEqual(int(balance_last), int(balance_1st) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            i += 1023
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1023))

        # write too large entry
        name_1 = create_random_string(2)
        name_2 = create_random_string(2)

        self.assertTrue("Entry cannot be larger than 10KB" in self.factom_chain_object.add_entries_to_chain(self.entry_creds_wallet1, path, chain_id, name_1, name_2))

        # validate get firstentry command
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry(chain_id))

        # validate get firstentry_with_entryhash command
        self.assertTrue("ExtID: " + firstentry_ext_id in self.factom_chain_object.get_firstentry_with_entryhash(chain_id))

        # validate get allentries command
        self.assertTrue("Entry [0]" in self.factom_chain_object.get_allentries(chain_id))

        os.remove(path)

    def test_compose_entry(self):
        # create chain
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)

        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            path = fout.name
        text = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet1, path, name_1, name_2)
        chain_id = text.split('\n')[1].split(' ')[1]

        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        text = self.factom_chain_object.compose_entry_from_binary_file(self.entry_creds_wallet1, path, chain_id,
                                                                       name_1, name_2)
        self.assertTrue("commit-entry" in text)
        self.assertTrue("reveal-entry" in text)

        os.remove(path)
