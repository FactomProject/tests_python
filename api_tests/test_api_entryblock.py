import unittest

from nose.plugins.attrib import attr

from api_objects.factomd_api_objects import FactomApiObjects
from helpers.helpers import read_data_from_json
from api_objects.factom_wallet_api_objects import FactomWalletApiObjects


@attr(last=True)
class FactomAPIEntryBlockTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]

    def setUp(self):
        self.factom_api = FactomApiObjects()
        self.factom_api_wallet = FactomWalletApiObjects()

    def test_ansible_entries(self):
        self._missing_entries(self.factomd_address)

    def _missing_entries(self, factomd_address):
        self.factom_api.change_factomd_address(factomd_address)
        dblock_keymr = self.factom_api.get_directory_block_head()
        print dblock_keymr
        result =self.factom_api.get_directory_block_by_keymr(dblock_keymr)
        print result
        #self.factom_api.get_entry_block(entryblock_keymr)








