import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
import re


@attr(last=True)
class FactomHeightTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5']
                                   ,data['factomd_address_6']]

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()


    def test_current_directory_block_height_of_all_nodes(self):
        directory_block_head_1 = self.factom_chain_object.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                directory_block_head_2 = self.factom_chain_object.get_directory_block_height_from_head()
                self.assertTrue(directory_block_head_1 == directory_block_head_2,
                                "mismatch in directory block at height - %s on server - %s" % (directory_block_head_2,factomd_address_custom))

    def test_get_heights_of_all_nodes(self):
        get_height_1 = self.factom_chain_object.get_heights()
        for factomd_address_custom in self.factomd_address_custom_list:
            self.factom_chain_object.change_factomd_address(factomd_address_custom)
            get_height_2 = self.factom_chain_object.get_heights()
            self.assertTrue(get_height_1 == get_height_2), "mismatch in heights on server - %s" % factomd_address_custom
