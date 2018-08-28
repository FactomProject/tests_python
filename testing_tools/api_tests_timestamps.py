import unittest

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json

@attr(production=True)
class APITestsTimestamps(unittest.TestCase):
    # testcases to verify the various timestamps in entry credit block and entry block
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    data = read_data_from_json('addresses.json')
    factomd_address = data['localhost']

    def setUp(self):
        pass

    def test_entrycredit_block_timestamp(self):
        '''
        testcase to verify the timestamps of entries in entry credit block are in the defined range
        steps: get the height
        get the directory block timestamp and convert to unix time
        get the timestamp of the entries in entry credit block
        compare the above time stamps
        Entry credit block timestamp are allowed to be within 2 hrs range of directory block timestamp
        '''
        self.api_factomd.change_factomd_address(self.factomd_address)
        height = self.api_factomd.get_heights()
        for i in range(height['directoryblockheight'],0,-1):
            dblock_time = self.api_factomd.get_directory_block_by_height(i)['header']['timestamp'] * 60

            #inconsistency in the production blockchain. There are no ecblocks from 70410-70387
            if (i > 70411 and i < 70386):
                ec_block = self.api_factomd.get_entry_credit_block_by_height(i)
                no_of_entries = len(ec_block['Body']['Entries'])
                for j in range(0,no_of_entries-1):
                    if "MilliTime" in ec_block['Body']['Entries'][j]:
                        entries_ecblock_time = int(ec_block['Body']['Entries'][j]['MilliTime'],16)/1000
                        self.assertFalse(entries_ecblock_time > dblock_time + 3600 or entries_ecblock_time < dblock_time - 3600,"Entry Credit Block has entry hashes more than 2 hrs range. height = %s" % str(i))

    def test_entry_block_time(self):
        '''
        testcase to verify the entries in entry block are within 10 mins of the directory block time
        steps: get the height
        get the directory block timestamp and convert to unix time
        get the keymr of the entry block from the directory block
        get the entryblock using the keymr as input
        get the timestamp of the entries in entry block and convert to unix time
        compare the above two time stamps. it should be no more than 10 mins of directory block timestamp
        '''
        self.api_factomd.change_factomd_address(self.factomd_address)
        height = self.api_factomd.get_heights()
        for i in range(height['directoryblockheight'],0, -1):
            dblock_time = self.api_factomd.get_directory_block_by_height(i)['header']['timestamp'] * 60
            dbentries = self.api_factomd.get_directory_block_by_height(i)['dbentries']
            if len(dbentries) > 3:
                for j in range(3,len(dbentries)):
                    entryblock_keymr = dbentries[j]['keymr']
                    for k in range(0, len(self.api_factomd.get_entry_block(entryblock_keymr)['entrylist'])):
                        self.assertFalse(self.api_factomd.get_entry_block(entryblock_keymr)['entrylist'][k]['timestamp'] > dblock_time + 600, "Entry Blocks are 10 mins more than the Directory Blockat height %s" % i)