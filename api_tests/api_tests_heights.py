import unittest

from nose.plugins.attrib import attr

from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json


@attr(last=True)
class APITestsHeights(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]

    def setUp(self):
        self.api = APIObjectsFactomd()
        self.api_wallet = APIObjectsWallet()

    def test_check_admin_block_height(self):
        blocks = self.api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.api.change_factomd_address(self.factomd_address)
                admin_block_height = self.api.get_admin_block_by_height(x)
                self.api.change_factomd_address(factomd_address_custom)
                admin_block_height_1 = self.api.get_admin_block_by_height(x)
                self.assertTrue(admin_block_height == admin_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_check_directory_block_height(self):
        blocks = self.api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.api.change_factomd_address(self.factomd_address)
                dblock_height = self.api.get_directory_block_by_height(x)
                self.api.change_factomd_address(factomd_address_custom)
                dblock_height_1 = self.api.get_directory_block_by_height(x)
                self.assertTrue(dblock_height == dblock_height_1,"mismatch in directory block at height %d" % (x))

    def test_check_entrycredit_block_height(self):
        blocks = self.api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.api.change_factomd_address(self.factomd_address)
                entrycredit_block_height = self.api.get_entry_credit_block_by_height(x)
                self.api.change_factomd_address(factomd_address_custom)
                entrycredit_block_height_1 = self.api.get_entry_credit_block_by_height(x)
                self.assertTrue(entrycredit_block_height == entrycredit_block_height_1,
                                "mismatch in entrycredit block at height %d" % (x))

    def test_check_factoid_block_height(self):
        blocks = self.api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.api.change_factomd_address(self.factomd_address)
                factoid_block_height = self.api.get_factoid_block_by_height(x)
                self.api.change_factomd_address(factomd_address_custom)
                factoid_block_height_1 = self.api.get_factoid_block_by_height(x)
                self.assertTrue(factoid_block_height == factoid_block_height_1,
                                "mismatch in factoid block at height %d" % (x))

    def test_wallet_height(self):
        blocks = self.api.get_heights()
        directory_block_height = blocks['directoryblockheight']
        # transactions need to be listed for wallet to catch up the directory block height
        listtxs = self.api_wallet.list_all_transactions_in_factoid_blockchain()
        wallet_height = (self.api_wallet.get_wallet_height()["height"])
        self.assertTrue(directory_block_height == wallet_height, "mismatch in wallet height")
