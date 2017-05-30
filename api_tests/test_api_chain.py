import unittest
import random
import string

from nose.plugins.attrib import attr

from api_objects.factomd_api_objects import FactomApiObjects
from helpers.helpers import read_data_from_json
from api_objects.factom_wallet_api_objects import FactomWalletApiObjects


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

    def test_make_chains_entries(self):
        chain_name = "first chain"
        ext_ids = "abcd"
        content = "hello world"
        self.make_transaction()
        result = self.wallet_api_objects.compose_chain(chain_name,ext_ids,content,self.entry_creds_wallet2)
        print result



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