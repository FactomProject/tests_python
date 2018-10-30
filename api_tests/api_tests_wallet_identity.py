import unittest, string, random, time

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class ApiTestsWallet(unittest.TestCase):
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    WAITTIME = 300
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        public_keys = self.api_wallet.import_addresses(
            self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        self.first_address = public_keys[0]
        self.entry_creds_wallet = public_keys[1]
        self.second_address = self.api_wallet.generate_factoid_address()
        self.entry_creds_wallet2 = self.api_wallet.generate_ec_address()


    def test_identity_key(self):
        keys = self.api_wallet.generate_identity_key()
        result =  self.api_wallet.identity_key(keys['public'])
        if result['secret'] == keys['secret']:
            print "keys matched"


    def test_all_identity_keys(self):
        result = self.api_wallet.all_identity_keys()
        print result
