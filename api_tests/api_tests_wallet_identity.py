import unittest, string, random, time

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address
from helpers.api_methods import generate_random_external_ids_and_content

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
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)


    def test_identity_key(self):
        keys = self.api_wallet.generate_identity_key()
        result =  self.api_wallet.identity_key(keys['public'])
        if result['secret'] == keys['secret']:
            print "keys matched"


    def test_all_identity_keys(self):
        result = self.api_wallet.all_identity_keys()
        print result


    def test_remove_identity_keys(self):
        #generate identity key
        keys = self.api_wallet.generate_identity_key()

        #remove the generated key
        self.api_wallet.remove_identity_keys(keys['public'])

        #list all the identity key
        identity_list = self.api_wallet.all_identity_keys()

        #flag to confirm the key is found
        found = False

        #check if the check is found in the list of identity keys. pass if not found. fail if found.
        for i in range(0,len(identity_list['keys'])):
            if identity_list['keys'][i]['public'] == keys['public']:
                found = True

        if found == False:
            print "Remove Identity Key Passed"
        else:
            print "Remove Identity Key Failed"



    def test_compose_identity_chain(self):
        chain_external_ids, content = generate_random_external_ids_and_content()
        keys = self.api_wallet.generate_identity_key()
        # compose chain
        compose = self.api_wallet.compose_identity_chain(chain_external_ids, keys['public'], self.entry_credit_address1000)
        print compose

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])
        print commit

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])
        print reveal





