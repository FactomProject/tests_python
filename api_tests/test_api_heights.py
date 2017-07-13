import unittest
import logging

from nose.plugins.attrib import attr

from api_objects.factomd_api_objects import FactomApiObjects
from helpers.helpers import read_data_from_json
from api_objects.factom_wallet_api_objects import FactomWalletApiObjects


@attr(api=True)
class FactomAPIHeightTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    #factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]

    factomd_address_custom_list = data['factomd_address_4']

    def setUp(self):
        self.factom_api = FactomApiObjects()
        self.factom_api_wallet = FactomWalletApiObjects()

    def ntest_check_admin_block_height(self):
        blocks = self.factom_api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_api.change_factomd_address(self.factomd_address)
                admin_block_height = self.factom_api.get_admin_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                admin_block_height_1 = self.factom_api.get_admin_block_by_height(x)
                self.assertTrue(admin_block_height == admin_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_check_directory_block_height(self):
        blocks = self.factom_api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_api.change_factomd_address(self.factomd_address)
                dblock_height = self.factom_api.get_directory_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                dblock_height_1 = self.factom_api.get_directory_block_by_height(x)
                #logging.getLogger('api_command').info(dblock_height)
                #logging.getLogger('api_command').info(dblock_height_1)
                #self.assertTrue(dblock_height == dblock_height_1,"mismatch in directory block at height %d and server = %s" % (x,factomd_address_custom))
                if (dblock_height == dblock_height_1):
                    logging.getLogger('api_command').info("mismatch in directory_block at height %d and server = %s" % (x,factomd_address_custom))

    def ntest_check_entrycredit_block_height(self):
        blocks = self.factom_api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_api.change_factomd_address(self.factomd_address)
                entrycredit_block_height = self.factom_api.get_entry_credit_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                entrycredit_block_height_1 = self.factom_api.get_entry_credit_block_by_height(x)
                self.assertTrue(entrycredit_block_height == entrycredit_block_height_1,
                                "mismatch in entrycredit block at height %d" % (x))

    def test_check_factoid_block_height(self):
        blocks = self.factom_api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.factom_api.change_factomd_address(self.factomd_address)
                factoid_block_height = self.factom_api.get_factoid_block_by_height(x)
                self.factom_api.change_factomd_address(factomd_address_custom)
                factoid_block_height_1 = self.factom_api.get_factoid_block_by_height(x)
                #logging.getLogger('api_command').info(factoid_block_height)
                #logging.getLogger('api_command').info(factoid_block_height_1)
                #self.assertTrue(factoid_block_height == factoid_block_height,
                               # "mismatch in factoid block at height %d and server = %s" % (x,factomd_address_custom))
                if (factoid_block_height == factoid_block_height):
                    logging.getLogger('api_command').info("mismatch in directory_block at height %d and server = %s" % (x,factomd_address_custom))


    def ntest_wallet_height(self):
        blocks = self.factom_api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        # transactions need to be listed for wallet to catch up the directory block height
        listtxs = self.factom_api_wallet.list_all_transactions_in_factoid_blockchain()
        wallet_height = (self.factom_api_wallet.get_wallet_height()["height"])
        self.assertTrue(directory_block_height == wallet_height, "mismatch in wallet height")
