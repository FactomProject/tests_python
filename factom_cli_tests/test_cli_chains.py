import unittest
import os
import time

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string

class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(
            "Fs2DNirmGDtnAZGXqca3XHkukTNMxoMGFFQxJA3bAjJnKzzsZBMH")
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            'Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def test_make_chain_with_wrong_address(self):
        path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
        self.assertTrue("not an Entry" in self.factom_chain_object.make_chain_from_binary_file('bogus', path, '1', '1'))

    def test_make_chain_with_factoids_not_ec(self):
        path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
        self.assertTrue("not an Entry" in self.factom_chain_object.make_chain_from_binary_file(self.first_address, path,
                                                                                               '1', '1'))

    def test_make_correct_chain_with_not_enough_ec(self):
        path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
        self.assertTrue(
            'Not enough Entry Credits' in self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2,
                                                                                               path, '2', '2'))

    def test_make_chain_that_allredy_exist(self):
        path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
        print self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet2, '100')
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        time.sleep(2)
        print self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1, name_2)
        print self.entry_creds_wallet2
        print self.first_address
        self.assertTrue('already exist' in self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1, name_2))

    def test_make_chain_and_check_balance(self):
        path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
        self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet2, '100')
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet2, path, name_1, name_2)

    def test_check_chain_height(self):
        seq = self.factom_chain_object.get_sequence_number_from_head()
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        self.assertTrue(seq == directory_block_height, 'Directory block is not equal to sequence')





