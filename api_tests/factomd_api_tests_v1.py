from api_objects.factomd_api_objects_v1 import FactomApiObjectsv1
from api_objects.factomd_api_objects import FactomApiObjects
import unittest
import os

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string

class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_api_v1 = FactomApiObjectsv1()
        self.factom_api = FactomApiObjects()


    def test_get_blocks_by_heights(self):
        '''
        test heights. compare with the v1 and v2 output
        '''
        directory_block_height_v1 = self.factom_api_v1.get_heights()
        directory_block_height = (self.factom_api.get_heights())['entryheight']
        self.assertTrue(directory_block_height_v1 == directory_block_height)

    def directoy_blocks(self):
        '''
        test the keymr of the directory block head
        '''
        keymr = self.factom_api_v1.get_directory_block_head()
        self.assertTrue('000000000000000000000000000000000000000000000000000000000000000a' ==
                       self.factom_api_v1.get_directory_block_by_keymr(keymr)['ChainID'])

    