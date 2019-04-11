import unittest, os, binascii, hashlib, time
from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from api_objects.api_objects_factomd import APIObjectsFactomd

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address

@attr(fast=True, flaky=True)
class CLITestsChains(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    blocktime = int(os.environ['BLOCKTIME'])

    TIME_TO_WAIT = 5

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.cli_chain = CLIObjectsChain()
        self.api_factomd = APIObjectsFactomd()
        self.ecrate = self.cli_create.get_entry_credit_rate()
        imported_addresses = self.cli_create.import_addresses(self.data['factoid_wallet_address'],
                                                              self.data['ec_wallet_address'])
        self.first_address = imported_addresses[0]
        self.entry_credit_address = imported_addresses[1]

    def test_raw_commit(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        # chain_flag_list = ['-T']
        text = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list)
        chain_dict = self.cli_chain.parse_simple_data(text)
        chain_id = chain_dict['ChainID']
        tx_id = chain_dict['CommitTxID']
        # tx_id = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
        wait_for_ack(tx_id)
        raw = self.cli_create.get_raw(tx_id)
        wait_for_ack(tx_id)

        # exclude public key and signature (last 32 + 64 bytes = 192 characters)
        raw_trimmed = raw[:-192]

        # convert to binary
        serialized_raw = binascii.unhexlify(raw_trimmed)

        # hash via SHA256
        hashed256_raw = hashlib.sha256(serialized_raw).hexdigest()

        self.assertEqual(hashed256_raw, tx_id, 'Raw data string is not correct')

