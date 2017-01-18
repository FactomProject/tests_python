import unittest
import string
import random
import time

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json


#script to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
class FactomHeightTests(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()

    def test_check_admin_block_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        for x in range(0, int(directory_block_height)):
            admin_block_height = self.factom_chain_object.get_admin_block_height(str(x))
            admin_block_height_1 = self.factom_multiple_nodes.get_admin_block_height_custom(str(x))
            self.assertTrue(admin_block_height == admin_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_check_directory_block_height(self):
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()
        for x in range(0, int(directory_block_head)):
            directory_block_height = self.factom_chain_object.get_directory_block_height(str(x))
            directory_block_height_1 = self.factom_multiple_nodes.get_directory_block_height_custom(str(x))
            self.assertTrue(directory_block_height == directory_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_check_entrycredit_block_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        for x in range(0, int(directory_block_height)):
            entrycredit_block_height = self.factom_chain_object.get_entrycredit_block_height(str(x))
            entrycredit_block_height_1 = self.factom_multiple_nodes.get_entrycredit_block_height_custom(str(x))
            self.assertTrue(entrycredit_block_height == entrycredit_block_height_1, "mismatch in entrycredit block at height %d" % (x))

    def test_check_factoid_block_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        for x in range(0, int(directory_block_height)):
            factoid_block_height = self.factom_chain_object.get_factoid_block_height(str(x))
            factoid_block_height_1 = self.factom_multiple_nodes.get_factoid_block_height_custom(str(x))
            self.assertTrue(factoid_block_height == factoid_block_height_1, "mismatch in factoid block at height %d" % (x))


