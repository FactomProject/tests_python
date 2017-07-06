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

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()

    @attr(production=True)
    def test_production_entries(self):
        self._missing_entries(self.factomd_address_prod)

    @attr(fast=True)
    def test_ansible_entries(self):
        self._missing_entries(self.factomd_address_ansible)


    def _missing_entries(self, factomd_address):
        self.factom_cli_create.change_factomd_address(factomd_address)
        self.factom_multiple_nodes.change_factomd_address(factomd_address)
        self.factom_chain_object.change_factomd_address(factomd_address)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()

        # count the number of times entry is not found
        entrycount = 0
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
                        entrycontents = self.factom_chain_object.get_entry_by_hash(entryhash)
                        if (entrycontents == "Entry not found"):
                            entrycount += 1
        self.assertTrue(entrycount == 0, "Missing entries in the block chain, missing entries: "+ str(entrycount))
