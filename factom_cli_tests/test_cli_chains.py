import unittest
import os, binascii
import time

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from api_objects.factomd_api_objects import FactomApiObjects

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class FactomChainTests(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    ACK_WAIT_TIME = 20

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.factomd_api_objects = FactomApiObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(
            self.data['factoid_wallet_address'])
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet0 = self.factom_cli_create.create_entry_credit_address()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()
        text = self.factom_cli_create.force_buy_ec(self.first_address, self.entry_creds_wallet2, '1000')
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)

    def test_make_chain_with_wrong_address(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        self.assertTrue("is not an Entry Credit Public Address" in self.factom_chain_object.make_chain_from_binary_file('bogus', path, name_1, name_2), "Non-existent EC address not detected as such")

    def test_make_chain_with_factoids_not_ec(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        self.assertTrue("is not an Entry Credit Public Address" in self.factom_chain_object.make_chain_from_binary_file(self.first_address, path, name_1, name_2, "Factoid address used as EC address not detected"))

    def test_make_correct_chain_with_not_enough_ec(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        self.assertTrue(
            'Not enough Entry Credits' in self.factom_chain_object.make_chain_from_binary_file(
                self.entry_creds_wallet0, path, name_1, name_2, "Insufficient entry credits not detected"))

    def test_make_chain(self):
        # make 1st chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['known_chain_3_name']
        self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1)
        chain_ext_id = name_1
        hex_ext_id = binascii.hexlify(chain_ext_id)
        ext_id = self.data['known_chain_3_ext_id']
        self.factom_chain_object.add_entry_to_chain_by_hex_ext_id(self.entry_creds_wallet2, path, hex_ext_id, ext_id)

    def test_make_chain_that_already_exist(self):
        # make 1st chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1, name_2)

        # try to make duplicate chain
        self.assertTrue('already exist' in self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1, name_2), "Duplicate chain not detected")

    def test_make_chain_and_check_balance(self):
        CHAIN_AND_1K_ENTRY_COST = 12
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)

        balance_before = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)
        self.factom_chain_object.make_chain_from_binary_file_return_entry_hash(self.entry_creds_wallet2, path, name_1, name_2)
        balance_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)

        self.assertEqual(int(balance_before), int(balance_after) + CHAIN_AND_1K_ENTRY_COST, 'Incorrect charge for chain creation')

    def test_make_chain_with_hex_ext(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))

        tx_id = self.factom_chain_object.make_chain_from_binary_file_with_hex_ext_return_tx_id(self.entry_creds_wallet2,
                                                                                        path, name_1, name_2)
        wait_for_ack(tx_id, 20)
        self.assertTrue("TransactionACK" in self.factom_cli_create.request_transaction_acknowledgement(tx_id),
                        "Chain not created")

    def test_make_chain_return_chain_id(self):
        '''
        This test will only be effective the 1st time it is run as afterwards the chain will already exist.
        This structure is necessary because there is no other way to determine the success of the chain creation without a tx_id.
        '''
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['known_chain_2_name_1']
        name_2 = self.data['known_chain_2_name_2']

        chain_id = self.factom_chain_object.make_chain_from_binary_file_return_chain_id(self.entry_creds_wallet2,
                                                                                               path,
                                                                                               name_1, name_2)
        if ' ' in chain_id:
            chain_id = chain_id.split()[1]
        self.assertTrue("Entry not found" not in self.factom_chain_object.get_entryhash(self.data[
                                                                                            'known_chain_2_entry_hash']),
                        "Chain not created")
        self.assertTrue("EntryHash: " + self.data['known_chain_2_entry_hash'] in self.factom_chain_object.get_firstentry(chain_id), "Chain entry hash incorrect")

    def test_force_make_chain(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)

        tx_id = self.factom_chain_object.force_make_chain_from_binary_file_return_tx_id(self.entry_creds_wallet2,
                                                                                        path,
                                                                                        name_1, name_2)
        wait_for_ack(tx_id, 20)
        self.assertTrue("TransactionACK" in self.factom_cli_create.request_transaction_acknowledgement(tx_id),
                        "Chain not created")

    def test_quiet_make_chain(self):
        '''
        This test will be effective the 1st time it is run as afterwards the chain will already exist.
        This structure is necessary because there is no other way to determine the success of the chain creation without a tx_id.
         '''
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['known_chain_1_name_1']
        name_2 = self.data['known_chain_1_name_2']
        self.factom_chain_object.quiet_make_chain_from_binary_file(self.entry_creds_wallet2, path,
                                                                           name_1, name_2)
        self.assertTrue("Entry not found" not in self.factom_chain_object.get_entryhash(self.data['known_chain_1_entry_hash']))
        self.assertTrue("EntryHash: " +  self.data['known_chain_1_entry_hash'] in self.factom_chain_object.get_firstentry_by_ext_id(
            name_1, name_2))

    def test_compose_chain(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        text = self.factom_chain_object.compose_chain_from_binary_file(self.entry_creds_wallet1, path, name_1, name_2)
        balance = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        print 'balance', balance
        start = text.find('"message":"') + 11
        end = text.find('"},"method', start)
        self.factomd_api_objects.commit_chain_by_message(text[start:end])
        self.assertTrue("commit-chain" in text)
        self.assertTrue("reveal-chain" in text)

    def test_compose_chain(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        text = self.factom_chain_object.compose_chain_from_binary_file(self.entry_creds_wallet1, path, name_1, name_2)
        balance = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        print 'balance', balance
        start = text.find('"message":"') + 11
        end = text.find('"},"method', start)
        self.factomd_api_objects.commit_chain_by_message(text[start:end])
        self.assertTrue("commit-chain" in text)
        self.assertTrue("reveal-chain" in text)

    def test_check_chain_height(self):
        seq = self.factom_chain_object.get_sequence_number_from_head()
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        self.assertTrue(seq == directory_block_height, 'Directory block is not equal to sequence')








