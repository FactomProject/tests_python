import unittest
import time
import logging

from nose.plugins.attrib import attr
from collections import Counter

from api_objects.api_objects_factomd import APIObjectsFactomd
from helpers.helpers import read_data_from_json
from api_objects.api_objects_wallet import APIObjectsWallet


@attr(entryblock=True)
class FactomAPIEntryBlockTests(unittest.TestCase):
    '''
    testcases to verify entry hashes are same in entry credit block and entry block
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address_prod3']
    factomd_address_prod = data['factomd_address_prod3']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]
    entrylist_eblock = []
    entrylist_ecblock = []

    def setUp(self):
        self.factom_api = APIObjectsFactomd()
        self.factom_api_wallet = APIObjectsWallet()

    def test_ansible_entries(self):
        logging.getLogger('api_command').info("Execution Started")
        print "Execution Started"
        self.entrylist_eblock = self._fetch_entries_from_entryblock(self.factomd_address)
        self.entrylist_ecblock = self._fetch_entries_from_ecblock(self.factomd_address)
        list.sort(self.entrylist_eblock)
        list.sort(self.entrylist_ecblock)
        self.compare_lists(self.entrylist_eblock,self.entrylist_ecblock)
        print "end of first comparison"
        self.compare_lists(self.entrylist_ecblock,self.entrylist_eblock)
        #print "end of second comparison"
        #self.identify_duplicates(self.entrylist_eblock)
        #self.identify_duplicates(self.entrylist_ecblock)

    def notest_get_allentryhashes_from_entrycreditblock(self):
        self.entrylist_ecblock = self._fetch_entries_from_ecblock(self.factomd_address_prod)

    def _fetch_entries_from_entryblock(self, factomd_address):
        #self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        #for i in range(7500, height['entryblockheight']):
        for i in range(100005,100176):

            dblock_keymr = self.factom_api.get_directory_block_by_height(i)
            dblock =self.factom_api.get_directory_block_by_keymr(dblock_keymr['keymr'])
            if len(dblock) > 3:
                for x in range(3 , len(dblock)):
                    entry_block=self.factom_api.get_entry_block(dblock[x]['keymr'])
                    len_entrylist=len(entry_block['entrylist'])
                    for y in range(0, len_entrylist):
                        self.entrylist_eblock.append(entry_block['entrylist'][y]['entryhash'])
                        #print (entry_block['entrylist'][y]['entryhash'])
        logging.getLogger('api_command').info("Total Hashes in Entryblocks = %d" %len(self.entrylist_eblock))
        print "Total Hashes in Entryblocks = %d" %len(self.entrylist_eblock)
        time.sleep(5)
        #print self.entrylist_eblock
        return self.entrylist_eblock

    def _fetch_entries_from_ecblock(self,factomd_address):
        #self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        #for i in range(7500, height['directoryblockheight']):
        for i in range(100005,100176):

            ecblock = self.factom_api.get_entry_credit_block_by_height(i)
            len_entries = len(ecblock['body']['entries'])
            # check for entries more than 10 because there are 0 to 9 minute markers
            if len_entries > 10:
                for x in range(0,len_entries):
                    entries = ecblock['body']['entries'][x]
                    if 'entryhash' in entries:
                        self.entrylist_ecblock.append(ecblock['body']['entries'][x]['entryhash'])
                        #print(self.factom_api.get_entry_by_hash(ecblock['body']['entries'][x]['entryhash']))
                    #print "height = %s" % i
                    #print "-------------"
        logging.getLogger('api_command').info("Total Entryhashes in ECBLOCK = %d" % len(self.entrylist_ecblock))
        print "Total EntryCredit Blocks=%d" %len(self.entrylist_ecblock)
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
                    #if 'entryhash' in entries:
                        #print "ECBLOCK ------- Height = %s Entryhash = %s, EntryCredits = %s" % (i, entries['entryhash'], entries['credits'])

    def identify_duplicates(self,duplicatelist):
        a = dict(Counter(duplicatelist))
        sum = 0
        print "Duplicates in the list"
        for hash, value in a.iteritems():
            if value > 1:
                #print "Hash=%s # of times repeated = %s" %(hash,value)
                sum = sum + value
        print sum
        print "End of Duplicate function"

    def compare_lists(self,list1,list2):
        #list.sort(list1)
        #list.sort(list2)
        #for a in list1:
          #  print a
        #print "end of list1"
        #for a in list2:
         #   print a
        #print "end of list2"
        print "Start of Comparison Function"
        for a in list1:
            if a not in list2:
                print a
        print "End of Comparison Function"