import unittest

from nose.plugins.attrib import attr

from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import read_data_from_json
import json
import re


class CLITestsEntryBlock(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address_prod = data['factomd_address_prod2']
    factomd_address_ansible = data['factomd_address']

    def setUp(self):
        self.chain_objects = CLIObjectsChain()
        self.cli_create = CLIObjectsCreate()

    @attr(production_tool=True)
    def test_production_entries(self):
        self._missing_entries(self.factomd_address_prod)

    @attr(local_tool=True)
    def test_ansible_entries(self):
        self._missing_entries(self.factomd_address_ansible)


    def _missing_entries(self, factomd_address):
        self.cli_create.change_factomd_address(factomd_address)
        self.chain_objects.change_factomd_address(factomd_address)
        directory_block_head = self.chain_objects.get_directory_block_height_from_head()

        # count the number of times entry is not found
        entrycount = 0
        for x in range(0, int(directory_block_head)):
            dblock = json.loads(self.chain_objects.get_directory_block_by_height(x))
            if len(dblock['dblock']['dbentries']) > 3:
                totalentryblocks = len(dblock['dblock']['dbentries'])
                for x in range(3, totalentryblocks):
                    keymr = dblock['dblock']['dbentries'][x]['keymr']
                    entryblock =  self.chain_objects.get_entry_block(keymr)
                    entryblock = "".join(entryblock.split())
                    pattern = re.compile('EntryHash.{64}')
                    entryblocklist = pattern.findall(entryblock)
                    for entryhash in entryblocklist:
                        entryhash = entryhash.replace("EntryHash","")
                        entrycontents = self.chain_objects.get_entry_by_hash(entryhash)
                        if (entrycontents == "Entry not found"):
                            entrycount += 1
        self.assertTrue(entrycount == 0, "Missing entries in the block chain, missing entries: "+ str(entrycount))
