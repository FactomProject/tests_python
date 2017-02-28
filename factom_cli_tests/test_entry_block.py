import unittest
import math

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
import ast
import re
import datetime
import timeit
import __builtin__
__builtin__.__dict__.update(locals())

class FactomEntryTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')

    factomd_address_prod = data['factomd_windows_laptop']
    factomd_address_ansible = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                   data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                   data['factomd_address_6']]


    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        self.missingentrycount = 0

    #@attr(production=True)
    def notest_production_entries(self):
        self.missingentrycount = self._missing_entries(self.factomd_address_prod)
        print self.missingentrycount

    @attr(fast=True)
    def notest_ansible_entries(self):
        for factomd_address_custom in self.factomd_address_custom_list:
            self._missing_entries(factomd_address_custom)
            print "total entrycount missing = %d on the server = %s" % (self.entrycount, factomd_address_custom)
            self.entrycount = 0


    def _missing_entries(self, factomd_address):
        self.factom_cli_create.change_factomd_address(factomd_address)
        self.factom_multiple_nodes.change_factomd_address(factomd_address)
        self.factom_chain_object.change_factomd_address(factomd_address)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()
        totalentries = 0
        for x in range(0, int(directory_block_head)):
            directory_block_height = self.factom_chain_object.get_directory_block_height(str(x))
            directory_block_height = ast.literal_eval(directory_block_height)
            if len(directory_block_height['dblock']['dbentries']) > 3:
                totalentryblocks = len(directory_block_height['dblock']['dbentries'])
                for x in range(3, totalentryblocks):
                    keymr = directory_block_height['dblock']['dbentries'][x]['keymr']
                    entryblock =  self.factom_chain_object.get_entry_block(keymr)
                    entryblock = "".join(entryblock.split())
                    pattern = re.compile('EntryHash.{64}')
                    entryblocklist = pattern.findall(entryblock)
                    for entryhash in entryblocklist:
                        entryhash = entryhash.replace("EntryHash","")
                        self.entrycontents = self.factom_chain_object.get_entryhash(entryhash)
                        if (self.entrycontents == "Entry not found"):
                            self.entrycount += 1
                        totalentries += 1
                        #self.assertFalse(entrycontents == "Entry not found", ("missing entries %d" % entrycount))
        print "totalentries %d" % totalentries
        return self.entrycount
        #self.assertTrue(entrycount == 0, "Missing entries in the block chain, missing entries: "+ str(entrycount))


    def notest_get_heights_of_all_nodes(self):
        for factomd_address_custom in self.factomd_address_custom_list:
            self.factom_chain_object.change_factomd_address(factomd_address_custom)
            result = self.factom_chain_object.get_heights()
            print "height of server : %s" % factomd_address_custom
            print result

    def test_fetch_entries(self):
        delta = []
        entryhash = "0503fe82359416fc8caecc4a33fbbe94b78f02929e91cbbd022a3c5cab685f6b"
        self.factom_chain_object.change_factomd_address(self.factomd_address_prod)
        for j in range(1,100):
            starttime = datetime.datetime.now()
            print "Iteration %d, time before for loop begins %s" % (j, str(starttime))
            for x in range(1,10000 ):
                result = self.factom_chain_object.get_entryhash(entryhash)
            endtime = datetime.datetime.now()
            print "Iteration %d, time after for loop begins %s" % (j, str(endtime))
            diff = (endtime - starttime).total_seconds()
            delta.append(diff)
            print diff
        print delta
        print "average %f for CLI test" % (math.fsum(delta)/len(delta))


