import unittest

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_multiple_nodes import CLIObjectsMultipleNodes
from cli_objects.cli_objects_chain import CLIObjectsChain
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json

class APITestsChainhead(unittest.TestCase):
    data = read_data_from_json('addresses.json')
    factomd_address_prod = data['factomd_address_prod3']
    factomd_address_ansible = data['factomd_address']

    def setUp(self):
        self.factomd_api = APIObjectsFactomd()
        self.walletd_api = APIObjectsWallet()
        self.chainlist = {}

    @attr(production=True)
    def test_production_chains(self):
        self._verify_chains_api(self.factomd_address_prod)

    @attr(fast=False)
    def test_ansible_chains(self):
        self._verify_chains_api(self.factomd_address_ansible)


    def _verify_chains_api(self, factomd_address):
        self.factomd_api.change_factomd_address(factomd_address)
        directory_block_head = self.factomd_api.get_directory_block_head()
        directory_block_height = self.factomd_api.get_directory_block_by_keymr(directory_block_head)['header']['sequencenumber']
        for x in range(directory_block_height, 0 , -1):
            dblock = self.factomd_api.get_directory_block_by_height(x)
            if len(dblock['dbentries']) > 3:
                totalentryblocks = len(dblock['dbentries'])
                for x in range(3, totalentryblocks):
                    chainid = dblock['dbentries'][x]['chainid']
                    if chainid not in self.chainlist:
                        keyMR = dblock['dbentries'][x]['keymr']
                        chainhead = self.factomd_api.get_chain_head_by_chain_id(chainid)
                        self.assertEqual(keyMR, chainhead, 'Problematic KeyMR: ' + keyMR + " problematic chainhead: "
                                     + chainhead)
                        self.chainlist[chainid] = keyMR


