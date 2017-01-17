import unittest
import string
import random
import time

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string, read_data_from_json

class FactomHeightTests(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()

    def test_check_chain_height(self):
        #seq = self.factom_chain_object.get_sequence_number_from_head()
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        factoid_block_height = self.factom_chain_object.get_factoid_block_height_from_head(directory_block_height)
        print factoid_block_height
      #  self.assertTrue(seq == directory_block_height, 'Directory block is not equal to sequence')


