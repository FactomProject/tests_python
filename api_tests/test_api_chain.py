import unittest
import random
import string

from nose.plugins.attrib import attr

from api_objects.factomd_api_objects import FactomApiObjects
from helpers.helpers import read_data_from_json
from api_objects.factom_wallet_api_objects import FactomWalletApiObjects


from api_objects.factom_chains_objects import FactomApiChainObjects
from api_objects.general_objects import FactomGeneralObjects

@attr(last=True)
class FactomAPIEntryTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    address = read_data_from_json('addresses.json')
    factomd_address = address['factomd_address']
    factomd_address_custom_list = [address['factomd_address_0'], address['factomd_address_1'], address['factomd_address_2'],
                                   address['factomd_address_3'], address['factomd_address_4'], address['factomd_address_5'], address['factomd_address_6']]
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factomd_api_objects = FactomApiObjects()
        self.wallet_api_objects = FactomWalletApiObjects()
        self.first_address = self.wallet_api_objects.import_addres_by_secret(self.data['factoid_wallet_address'])
        self.entry_creds_wallet2 = self.wallet_api_objects.import_addres_by_secret(self.data['ec_wallet_address'])
        self.ecrate = self.factomd_api_objects.get_entry_credits_rate()
        self.factom_chain_object = FactomApiChainObjects()
        self.general_objects = FactomGeneralObjects()

    def notest_make_chains_entries(self):
        ext_ids = ["abcd","1111"]
        content = "35746820656e747279"
        #self.make_transaction()
        result = self.wallet_api_objects.compose_chain(ext_ids,content,self.entry_creds_wallet2)
        message = result['result']['commit']['params']['message']
        entry =  result['result']['reveal']['params']['entry']
        result = self.factomd_api_objects.commit_chain_by_message(message)
        result = self.factomd_api_objects.reveal_chain_by_entry(entry)
        entryhash = result['entryhash']
        result = self.factomd_api_objects.get_entry_by_hash(entryhash)
        self.assertFalse('Entry not found' in result)


    def make_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, 1)
        self.wallet_api_objects.add_entry_credits_output_to_transaction(transaction_name, self.entry_creds_wallet2, 1)
        self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        result = self.factomd_api_objects.submit_factoid_by_transaction(transaction)
        print result


    def notest_make_entries(self):
        ext_ids = ["7665656e61","6e6577636861696e"]
        content = "hello world"
        #content = "1234"
        self.make_transaction()
        chainid="e9ef3fd9c11deffbf771142ef0560fb5c087eca0c913107512db6539bae25ce3"
        #ecpub="EC2DKSYyRcNWf7RS963VFYgMExo1824HVeCfQ9PGPmNzwrcmgm2r"
        result = self.wallet_api_objects.compose_entry(ext_ids,content,self.entry_creds_wallet2,chainid)
        print result

    def test_make_entries(self):
        privateECKey = "0000000000000000000000000000000000000000000000000000000000000000"
        if "0000000000000000000000000000000000000000000000000000000000000000" == privateECKey:
            print "Warning, using a non-unique private key.  Your Entry Credits can be used by others."
            print "Change privateECKey in this script to a random number"
        print "\nAdd Entry Credits to this key: " + self.factom_chain_object.ec_addresses_human()
        print "It currently has a balance of " + str(self.factom_chain_object.get_ec_balance())


        self.factom_chain_object.write_to_factomd()
        print "wrote " + self.factom_chain_object.get_entry_hash()
        print self.factom_chain_object.entryContent

