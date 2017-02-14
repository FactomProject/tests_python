from api_objects.factomd_api_objects import FactomApiObjects
import unittest

from nose.plugins.attrib import attr
import ast
from helpers.helpers import read_data_from_json

@attr(fast=True)
class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_api = FactomApiObjects()
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_address']
        self.factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                       data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                       data['factomd_address_6']]

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

    def test_entrycredit_block(self):
        result = self.factom_api.get_entry_credit_block_by_height(10)
        print result

    def test_entrycredit_block_height(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, directory_block_height):
                self.factom_api.change_factomd_address(self.factomd_address)
                entrycredit_block_height = self.factom_api.get_entry_credit_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                entrycredit_block_height_1 = self.factom_api.get_entry_credit_block_by_height(x)
                self.assertTrue(entrycredit_block_height == entrycredit_block_height_1,
                                "mismatch in entrycredit block at height %d" % (x))


    def test_directory_block_height(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, directory_block_height):
                self.factom_api.change_factomd_address(self.factomd_address)
                directory_block_height = self.factom_api.get_directory_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                directory_block_height_1 = self.factom_api.get_directory_block_by_height(x)
                self.assertTrue(directory_block_height == directory_block_height_1,
                                "mismatch in directory block at height %d" % (x))


    def test_admin_block_height(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, directory_block_height):
                self.factom_api.change_factomd_address(self.factomd_address)
                admin_block_height = self.factom_api.get_admin_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                admin_block_height_1 = self.factom_api.get_admin_block_by_height(x)
                self.assertTrue(admin_block_height == admin_block_height_1,
                                "mismatch in admin block at height %d" % (x))


    def test_factoid_block_height(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, directory_block_height):
                self.factom_api.change_factomd_address(self.factomd_address)
                factoid_block_height = self.factom_api.get_factoid_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                factoid_block_height_1 = self.factom_api.get_factoid_block_by_height(x)
                self.assertTrue(factoid_block_height == factoid_block_height_1,
                                "mismatch in factoid block at height %d" % (x))