import unittest

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers.helpers import read_data_from_json
import json


class CLITestsChainhead(unittest.TestCase):
    data = read_data_from_json('addresses.json')
    factomd_address_prod = data['factomd_address_prod2']
    factomd_address_ansible = data['factomd_address']

    def setUp(self):
        self.chain_objects = CLIObjectsChain()
        self.cli_create = CLIObjectsCreate()
        self.chainlist = {}

    @attr(last=True)
    def test_ansible_chains(self):
        self.verify_chains(self.factomd_address_ansible)

    @attr(production=True)
    def test_production_chains(self):
        # testing against courtesy node
        self.verify_chains(self.factomd_address_prod)






    def verify_chains(self, factomd_address):
        self.cli_create.change_factomd_address(factomd_address)
        self.chain_objects.change_factomd_address(factomd_address)

        # start at most recent directory block
        directory_block_head = self.chain_objects.get_directory_block_height_from_head()

        # work backwards through directory block chain
        for x in range(int(directory_block_head), 0, -1):
            dblock = json.loads(self.chain_objects.get_directory_block_by_height(x))

            # ignore 1st 3 entries in Entry Block which are administrative
            if len(dblock['dblock']['dbentries']) > 3:
                totalentryblocks = len(dblock['dblock']['dbentries'])
                for x in range(3, totalentryblocks):
                    chainid = dblock['dblock']['dbentries'][x]['chainid']

                    # only check most recent entry block for the chain
                    if chainid not in self.chainlist:

                        # compare keyMR for each chain found in entry block with chainhead from factomd
                        keyMR = dblock['dblock']['dbentries'][x]['keymr']
                        chainhead = self.chain_objects.get_chainhead(chain_id=chainid)
                        EBlock = self.chain_objects.parse_block_data(chainhead)['EBlock']
                        self.assertEqual(EBlock, keyMR, 'for chain ' +
chainid + ' chainhead ' + EBlock + ' does not match chain keyMR ' + keyMR + ' in entry block')

                        # once encountered, add chain to 'already checked' list
                        self.chainlist[chainid] = keyMR
