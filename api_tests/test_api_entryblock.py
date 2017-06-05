import unittest
import time

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
    factomd_address_prod = data['factomd_address_prod1']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]
    entrylist_eblock = []
    entrylist_ecblock = []

    def setUp(self):
        self.factom_api = FactomApiObjects()
        self.factom_api_wallet = FactomWalletApiObjects()

    def test_ansible_entries(self):
        self.entrylist_eblock = self._fetch_entries_from_entryblock(self.factomd_address_prod)
        #self.entrylist_ecblock = self._fetch_entries_from_ecblock(self.factomd_address_prod)
        #if (self.entrylist_eblock == self.entrylist_ecblock):
        #self._fetch_duplicates(self.entrylist_ecblock)
        #print len((set(self.entrylist_eblock) - set(self.entrylist_ecblock)))


    def _fetch_entries_from_entryblock(self, factomd_address):
        self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        #for i in range(7500, height['entryblockheight']):
        for i in range(53475,54000):
            dblock_keymr = self.factom_api.get_directory_block_by_height(i)
            dblock =self.factom_api.get_directory_block_by_keymr(dblock_keymr['keymr'])
            if len(dblock) > 3:
                for x in range(3 , len(dblock)):
                    entry_block=self.factom_api.get_entry_block(dblock[x]['keymr'])
                    len_entrylist=len(entry_block['entrylist'])
                    for y in range(0, len_entrylist):
                        self.entrylist_eblock.append(entry_block['entrylist'][y]['entryhash'])
                        #print (entry_block['entrylist'][y]['entryhash'])
        print len(self.entrylist_eblock)
        time.sleep(5)
        #print self.entrylist_eblock
        return self.entrylist_eblock

    def _fetch_entries_from_ecblock(self,factomd_address):
        self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        #for i in range(7500, height['directoryblockheight']):
        for i in range(53475, 54000):
            ecblock = self.factom_api.get_entry_credit_block_by_height(i)
            len_entries = len(ecblock['body']['entries'])
            if len_entries > 10:
                for x in range(0,len_entries):
                    entries = ecblock['body']['entries'][x]
                    if 'entryhash' in entries:
                        self.entrylist_ecblock.append(ecblock['body']['entries'][x]['entryhash'])
                        #print(self.factom_api.get_entry_by_hash(ecblock['body']['entries'][x]['entryhash']))
                    #print "height = %s" % i
                    #print "-------------"
        print len(self.entrylist_ecblock)
        time.sleep(5)
        #print self.entrylist_ecblock
        return self.entrylist_ecblock



    def notest_entry_block(self):
        height = self.factom_api.get_heights()
        for i in range(7500, height['directoryblockheight']):
            ecblock = self.factom_api.get_entry_credit_block_by_height(i)
            dblock_keymr = self.factom_api.get_directory_block_by_height(i)
            dblock = self.factom_api.get_directory_block_by_keymr(dblock_keymr['keymr'])
            if len(dblock) > 3:
                for x in range(3, len(dblock)):
                    entry_block = self.factom_api.get_entry_block(dblock[x]['keymr'])
                    len_entrylist = len(entry_block['entrylist'])
                    for y in range(0, len_entrylist):
                        print "EBLOCK ----  Height = %s EntryHash = %s" %(i,entry_block['entrylist'][y]['entryhash'])
            len_entries = len(ecblock['body']['entries'])
            if len_entries > 10:
                for x in range(0, len_entries):
                    entries = ecblock['body']['entries'][x]
                    if 'entryhash' in entries:
                        print "ECBLOCK ------- Height = %s Entryhash = %s, EntryCredits = %s" % (i, entries['entryhash'], entries['credits'])
