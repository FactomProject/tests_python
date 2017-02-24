import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
import ast
import re


class FactomEntryTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')

    factomd_address_prod = data['factomd_address_prod2']
    factomd_address_ansible = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                   data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                   data['factomd_address_6']]

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        self.entrycount = 0

    @attr(production=True)
    def notest_production_entries(self):
        self._missing_entries(self.factomd_address_prod)

    @attr(fast=True)
    def test_ansible_entries(self):
        for factomd_address_custom in self.factomd_address_custom_list:
            self._missing_entries(factomd_address_custom)
            print "total entrycount missing = %d on the server = %s" % (self.entrycount, factomd_address_custom)
            self.entrycount = 0


    def _missing_entries(self, factomd_address):
        self.factom_cli_create.change_factomd_address(factomd_address)
        self.factom_multiple_nodes.change_factomd_address(factomd_address)
        self.factom_chain_object.change_factomd_address(factomd_address)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()

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
                        #self.assertFalse(entrycontents == "Entry not found", ("missing entries %d" % entrycount))

        return self.entrycount
        #self.assertTrue(entrycount == 0, "Missing entries in the block chain, missing entries: "+ str(entrycount))


    def test_get_heights_of_all_nodes(self):
        for factomd_address_custom in self.factomd_address_custom_list:
            self.factom_chain_object.change_factomd_address(factomd_address_custom)
            result = self.factom_chain_object.get_heights()
            print "height of server : %s" % factomd_address_custom
            print result

