import unittest, re
from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.cli_methods import get_data_dump_from_nonansible_server
from helpers.helpers import read_data_from_json

@attr(api=True)
class APITests(unittest.TestCase):

    def setUp(self):
        self.factom_api = APIObjectsFactomd()
        self.wallet_api = APIObjectsWallet()
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_controlpanel']

    def test_directory_blocks(self):
        keymr = self.factom_api.get_directory_block_head()
        self.assertTrue('000000000000000000000000000000000000000000000000000000000000000a' ==
                        self.factom_api.get_directory_block_by_keymr(keymr)["entryblocklist"][0]['chainid'])

    def test_get_heights(self):
        self.assertTrue('entryheight' in self.factom_api.get_heights())

    def test_get_blocks_by_heights(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        self.assertTrue('keymr' in self.factom_api.get_directory_block_by_height(directory_block_height))

    def test_get_current_minute(self):
        datadump = get_data_dump_from_nonansible_server(self.factomd_address)
        datadumplist = datadump.split('/')
        temp = datadumplist[4]
        controlpanel_minute = int(re.search('[0-9]', temp).group())
        result = self.factom_api.get_current_minute()
        cli_minute = result['minute']
        diff =  cli_minute - controlpanel_minute
        self.assertFalse(diff > 2,"minutes are not matching")

    def test_get_factomd_properties(self):
        result = str(self.factom_api.get_factomd_properties())
        print 'result', result
        self.assertTrue('factomdversion' in result and 'factomdapiversion' in result, 'factomd properties command not working' )

    def test_get_wallet_properties(self):
        result = str(self.wallet_api.get_wallet_properties())
        self.assertTrue('walletversion' in result and 'walletapiversion' in result, 'wallet properties command not working' )

    def test_raw_commit(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-T']
        tx_id = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
        raw = self.cli_create.get_raw(tx_id)

        # exclude public key and signature (last 32 + 64 bytes = 192 characters)
        raw_trimmed = raw[:-192]

        # convert to binary
        serialized_raw = binascii.unhexlify(raw_trimmed)

        # hash via SHA256
        hashed256_raw = hashlib.sha256(serialized_raw).hexdigest()

        self.assertEqual(hashed256_raw, tx_id, 'Raw data string is not correct')



