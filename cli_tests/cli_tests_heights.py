import unittest

from nose.plugins.attrib import attr

from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_multiple_nodes import CLIObjectsMultipleNodes
from helpers.helpers import read_data_from_json

import time
import logging

@attr(last=True)
class CLITestsHeight(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]

    def setUp(self):
        self.chain_objects = CLIObjectsChain()
        self.cli_create = CLIObjectsCreate()
        self.multiple_nodes = CLIObjectsMultipleNodes()

    def test_check_admin_block_height(self):
        directory_block_height = self.chain_objects.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.chain_objects.change_factomd_address(self.factomd_address)
                admin_block_height = self.chain_objects.get_admin_block_by_height(x)
                self.chain_objects.change_factomd_address(factomd_address_custom)
                admin_block_height_1 = self.chain_objects.get_admin_block_by_height(x)
                self.assertTrue(admin_block_height == admin_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_check_directory_block_height(self):
        directory_block_head = self.chain_objects.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_head)):
                self.chain_objects.change_factomd_address(self.factomd_address)
                directory_block_height = self.chain_objects.get_directory_block_by_height(x)
                self.chain_objects.change_factomd_address(factomd_address_custom)
                directory_block_height_1 = self.chain_objects.get_directory_block_by_height(x)
                self.assertTrue(directory_block_height == directory_block_height_1,
                                "mismatch in directory block at height %d" % (x))

    def test_check_entrycredit_block_height(self):
        directory_block_height = self.chain_objects.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.chain_objects.change_factomd_address(self.factomd_address)
                entrycredit_block_height = self.chain_objects.get_entrycredit_block_by_height(x)
                self.chain_objects.change_factomd_address(factomd_address_custom)
                entrycredit_block_height_1 = self.chain_objects.get_entrycredit_block_by_height(x)
                self.assertTrue(entrycredit_block_height == entrycredit_block_height_1,
                                "mismatch in entrycredit block at height %d" % (x))

    def test_check_factoid_block_height(self):
        directory_block_height = self.chain_objects.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.chain_objects.change_factomd_address(self.factomd_address)
                factoid_block_height = self.chain_objects.get_factoid_block_by_height(x)
                self.chain_objects.change_factomd_address(factomd_address_custom)
                factoid_block_height_1 = self.chain_objects.get_factoid_block_by_height(x)
                self.assertTrue(factoid_block_height == factoid_block_height_1,
                                "mismatch in factoid block at height %d" % (x))

    def test_wallet_height(self):
        time.sleep(40)
        self.multiple_nodes.get_all_transactions()
        directory_block_height = self.chain_objects.get_directory_block_height_from_head()
        logging.getLogger('height').info(directory_block_height)
        # transactions need to be listed for wallet to catch up the directory block height
        self.multiple_nodes.get_all_transactions()
        self.multiple_nodes.get_all_transactions()
        wallet_height = self.multiple_nodes.get_wallet_height()
        logging.getLogger('height').info(wallet_height)
        self.assertTrue(directory_block_height == wallet_height, "mismatch in wallet height")
