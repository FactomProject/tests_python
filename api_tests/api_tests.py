from api_objects.factomd_api_objects import FactomApiObjects
import unittest

from nose.plugins.attrib import attr
import re

from helpers.factom_cli_methods import get_data_dump_from_nonansible_server
from helpers.helpers import read_data_from_json

@attr(api=True)
class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_api = FactomApiObjects()
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_controlpanel']

    def test_directory_blocks(self):
        keymr = self.factom_api.get_directory_block_head()
        self.assertTrue('000000000000000000000000000000000000000000000000000000000000000a' ==
                        self.factom_api.get_directory_block_by_keymr(keymr)['chainid'])
    def test_get_heights(self):
        self.assertTrue('entryheight' in self.factom_api.get_heights())

    def test_get_blocks_by_heights(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        self.assertTrue('keymr' in self.factom_api.get_directory_block_by_height(directory_block_height))

    def test_get_current_minute(self):
        datadump = get_data_dump_from_nonansible_server(self.factomd_address)
        datadumplist = datadump.split('/')
        minute = datadumplist[4]
        result = self.factom_api.get_current_minute()
        current_minute = result['minute']
        self.assertEqual(int(re.search('[0-9]', minute).group()),(int(current_minute)-1),"minutes are not matching")
