import unittest
import string
import random
import time
import os

from cli_objects.factom_cli_create import FactomCliCreate
from helpers.helpers import read_data_from_json, create_random_string
from cli_objects.factom_chain_objects import FactomChainObjects


class FactomCliEndToEndTest(unittest.TestCase):
    data = read_data_from_json('prod.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_address'])

    def test_make_chain_and_check_balance(self):

        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        height = self.factom_chain_object.get_directory_block_height_from_head()
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        chain_id = self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet1, path, name_1, name_2)
        hash =  self.factom_chain_object.add_entries_to_chain_and_receive_entry_hash(self.entry_creds_wallet1, path, chain_id, name_1, name_2)
        time.sleep(self.data['time_to_sleep'])
        self.factom_chain_object.change_factomd_address(self.data['factomd_2_address'])
        self.assertTrue('just_text' in self.factom_chain_object.get_entries_by_hash(hash), 'Cannot get entry')
        second_height = self.factom_chain_object.get_directory_block_height_from_head()
        self.assertTrue(second_height > height, 'Block height is not adjusted')

