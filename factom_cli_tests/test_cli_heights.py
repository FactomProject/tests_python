import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json


@attr(checkheight=True)
class FactomHeightTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address_1']
    #factomd_address_custom_list = [data['factomd_address'], data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
    #                               data['factomd_address_6'], data['factomd_address_7'], data['factomd_address_8'],
    #                               data['factomd_address_9'], data['factomd_address_10']]

    factomd_address_custom_list = [data['factomd_address_2'], data['factomd_address_3'],data['factomd_address_4'],
                                   data['factomd_address_5'],
                                    data['factomd_address_7'], data['factomd_address_8'],
                                   data['factomd_address_9'], data['factomd_address_10']]

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()

    def notest_check_admin_block_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_chain_object.change_factomd_address(self.factomd_address)
                admin_block_height = self.factom_chain_object.get_admin_block_height(str(x))
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                admin_block_height_1 = self.factom_chain_object.get_admin_block_height(str(x))
                self.assertTrue(admin_block_height == admin_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_check_directory_block_height(self):
        self.factom_chain_object.change_factomd_address(self.factomd_address)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_head)):
                self.factom_chain_object.change_factomd_address(self.factomd_address)
                directory_block_height = self.factom_chain_object.get_directory_block_height(str(x))
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                directory_block_height_1 = self.factom_chain_object.get_directory_block_height(str(x))
                self.assertTrue(directory_block_height == directory_block_height_1,
                                "mismatch in directory block at height %d, server = %s" % ((x), factomd_address_custom))

    def notest_check_entrycredit_block_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_chain_object.change_factomd_address(self.factomd_address)
                entrycredit_block_height = self.factom_chain_object.get_entrycredit_block_height(str(x))
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                entrycredit_block_height_1 = self.factom_chain_object.get_entrycredit_block_height(str(x))
                self.assertTrue(entrycredit_block_height == entrycredit_block_height_1,
                                "mismatch in entrycredit block at height %d" % (x))

    def notest_check_factoid_block_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_chain_object.change_factomd_address(self.factomd_address)
                factoid_block_height = self.factom_chain_object.get_factoid_block_height(str(x))
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                factoid_block_height_1 = self.factom_chain_object.get_factoid_block_height(str(x))
                self.assertTrue(factoid_block_height == factoid_block_height_1,
                                "mismatch in factoid block at height %d" % (x))

    def notest_wallet_height(self):
        directory_block_height = self.factom_chain_object.get_directory_block_height_from_head()
        # transactions need to be listed for wallet to catch up the directory block height
        listtxs = self.factom_multiple_nodes.get_all_transactions()
        wallet_height = self.factom_multiple_nodes.get_wallet_height()

        self.assertTrue(directory_block_height == wallet_height, "mismatch in wallet height")

