import unittest
import string
import random
import time

from nose.plugins.attrib import attr

from api_objects.factom_wallet_api_objects import FactomWalletApiObjects
from api_objects.factomd_api_objects import FactomApiObjects
from helpers.helpers import read_data_from_json

@attr(fast=True)
class FactomWalletApiTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.wallet_api_objects = FactomWalletApiObjects()
        self.factomd_api_objects = FactomApiObjects()
        self.first_address = self.wallet_api_objects.import_addres_by_secret(self.data['factoid_wallet_address'])
        self.second_address = self.wallet_api_objects.generate_factoid_address()
        self.ecrate = self.factomd_api_objects.get_entry_credits_rate()
        self.entry_creds_wallet2 = self.wallet_api_objects.import_addres_by_secret(self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.wallet_api_objects.generate_ec_address()

    def test_alocate_founds_to_factoid_walled_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_factoid_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_in_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.factomd_api_objects.submit_factoid_by_transaction(transaction)['message'])

    def test_alocate_too_small_founds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))


        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, 1)
        self.wallet_api_objects.add_factoid_output_to_transaction(transaction_name, self.second_address, 1)
        self.wallet_api_objects.subtract_fee_in_transaction(transaction_name, self.second_address)

        self.assertTrue('Error totalling Outputs: Amount is out of range' in
                        self.wallet_api_objects.sign_transaction(transaction_name)['error']['data'])

    def test_list_transactions_api_call(self):
        self.assertTrue('transactions' in self.wallet_api_objects.list_all_transactions_in_factoid_blockchain(),
                        'Transactions are not listed')

    def test_list_transaction_by_id(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_factoid_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_in_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        txid = self.factomd_api_objects.submit_factoid_by_transaction(transaction)['txid']
        time.sleep(10)
        self.assertTrue(self.wallet_api_objects.list_transactions_by_txid(txid)['transactions'][0]['inputs'][0]['amount']
                        == 100000000, 'Transaction is not listed')

    def test_list_current_working_transactions_in_wallet(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

        self.wallet_api_objects.delete_transaction(transaction_name)
        self.assertFalse(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_entry_credits_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_in_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        self.assertTrue("Successfully submitted" in self.factomd_api_objects.submit_factoid_by_transaction(transaction)['message'])

