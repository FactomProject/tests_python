from api_objects.factomd_api_objects import FactomApiObjects
import unittest
import os

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string

class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_api = FactomApiObjects()

    def test_directory_blocks(self):
        keymr = self.factom_api.get_directory_block_head()
        self.assertTrue('000000000000000000000000000000000000000000000000000000000000000a' ==
                        self.factom_api.get_directory_block_by_keymr(keymr)['chainid'])
    def test_get_heights(self):
        self.assertTrue('entryheight' in self.factom_api.get_heights())

    def test_get_blocks_by_heights(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        self.assertTrue('keymr' in self.factom_api.get_directory_block_by_height(directory_block_height))
