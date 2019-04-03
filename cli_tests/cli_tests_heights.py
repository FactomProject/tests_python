import unittest, time
import json

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import read_data_from_json

@attr(last=True)
class CLITestsHeight(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    api_factomd = APIObjectsFactomd()
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('addresses.json')
    data1 = read_data_from_json('shared_test_data.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]

    def setUp(self):
        pass

    def test_check_admin_block_height(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.cli_chain.change_factomd_address(self.factomd_address)
                admin_block_height = self.cli_chain.get_admin_block_by_height(x)
                self.cli_chain.change_factomd_address(factomd_address_custom)
                admin_block_height_1 = self.cli_chain.get_admin_block_by_height(x)
                self.assertTrue(admin_block_height == admin_block_height_1, "mismatch in admin block at height %d" % (x))

    def test_admin_block_height_suppress_raw_data(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        admin_block_height = self.cli_chain.get_admin_block_by_height(directory_block_height, '-r')
        self.assertNotIn('raw', admin_block_height, 'Raw data is not suppressed')

    def test_check_directory_block_height(self):
        directory_block_head = self.cli_chain.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_head)):
                self.cli_chain.change_factomd_address(self.factomd_address)
                directory_block_height = self.cli_chain.get_directory_block_by_height(x)
                self.cli_chain.change_factomd_address(factomd_address_custom)
                directory_block_height_1 = self.cli_chain.get_directory_block_by_height(x)
                self.assertTrue(directory_block_height == directory_block_height_1,
                                "mismatch in directory block at height %d" % (x))

    def test_directory_block_height_suppress_raw_data(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        direct_block_height = self.cli_chain.get_directory_block_by_height(directory_block_height, '-r')
        self.assertNotIn('raw', direct_block_height, 'Raw data is not suppressed')

    def test_check_entrycredit_block_height(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.cli_chain.change_factomd_address(self.factomd_address)
                entrycredit_block_height = self.cli_chain.get_entrycredit_block_by_height(x)
                self.cli_chain.change_factomd_address(factomd_address_custom)
                entrycredit_block_height_1 = self.cli_chain.get_entrycredit_block_by_height(x)
                self.assertTrue(entrycredit_block_height == entrycredit_block_height_1,
                                "mismatch in entrycredit block at height %d" % (x))

    def test_entrycredit_block_height_suppress_raw_data(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        entrycredit_block_height = self.cli_chain.get_entrycredit_block_by_height(directory_block_height, '-r')
        self.assertNotIn('raw', entrycredit_block_height, 'Raw data is not suppressed')

    def test_check_factoid_block_height(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        for factomd_address_custom in self.factomd_address_custom_list:
            for x in range(0, int(directory_block_height)):
                self.cli_chain.change_factomd_address(self.factomd_address)
                factoid_block_height = self.cli_chain.get_factoid_block_by_height(x)
                self.cli_chain.change_factomd_address(factomd_address_custom)
                factoid_block_height_1 = self.cli_chain.get_factoid_block_by_height(x)
                self.assertTrue(factoid_block_height == factoid_block_height_1,
                                "mismatch in factoid block at height %d" % (x))

    def test_factoid_block_height_suppress_raw_data(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        factoid_block_height = self.cli_chain.get_factoid_block_by_height(directory_block_height, '-r')
        self.assertNotIn('raw', factoid_block_height, 'Raw data is not suppressed')

    def test_wallet_height(self):
        time_waited = 0

        # touch wallet to get wallet height updated
        self.cli_create.get_all_transactions()

        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        wallet_height = self.cli_chain.get_wallet_height()

        # throw error if wallet doesn't sync up within 1 block
        while directory_block_height != wallet_height and time_waited < self.blocktime:
            time.sleep(1)
            self.cli_create.get_all_transactions()
            directory_block_height = self.cli_chain.get_directory_block_height_from_head()
            wallet_height = self.cli_chain.get_wallet_height()
            time_waited += 1
        self.assertEqual(directory_block_height, wallet_height, 'directory block height of ' + str(directory_block_height) + ' does not match wallet height of ' + str(wallet_height))



    def test_server_fault(self):
        directory_block_height = self.cli_chain.get_directory_block_height_from_head()
        for x in range(int(directory_block_height),0,-1):
            admin_block = self.cli_chain.get_admin_block_by_height(x)
            result = json.loads(admin_block)
            # print(result['ablock']['abentries'][0]['adminidtype'])

            for i in result['ablock']['abentries']:
                if(i['adminidtype']) != 1 and (i['adminidtype']) != 11 and (i['adminidtype']) != 5 and (i['adminidtype']) != 6 and (i['adminidtype']) != 14 and (i['adminidtype']) != 0 \
                        and (i['adminidtype']) != 8  and (i['adminidtype']) != 9 and (i['adminidtype']) != 13 and (i['adminidtype']) != 3 and (i['adminidtype']) != 7:
                    print "adminidtype " + str(i['adminidtype']) + " height:  " + str(x)


