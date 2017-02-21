from enterprisewallet_objects.entwallet_transactions_objects import EnterpriseWalletTransactionsbjects
from enterprisewallet_objects.entwallet_addressbook_objects import EnterpriseWalletAddressBookObjects
from cli_objects.factom_cli_create import FactomCliCreate
import unittest
from helpers.helpers import read_data_from_json
import time
from nose.plugins.attrib import attr

@attr(fast=True)
class EnterpriseWalletTransactionTests(unittest.TestCase):

    def setUp(self):
        self.entwallet_transactions_objects = EnterpriseWalletTransactionsbjects()
        self.entwallet_addressbook_objects = EnterpriseWalletAddressBookObjects()
        self.factom_cli_create = FactomCliCreate()

        data = read_data_from_json('wallet_addresses.json')
        self.address = data['factoid_public_wallet_address']
        self.ecaddress = data['ec_public_wallet_address']

    def test_list_alltransactions(self):
        result = self.entwallet_transactions_objects.get_transactions_from_enterprisewallet()
        print result


    def test_make_factoid_transaction_in_enterprisewallet(self):
        result = self.entwallet_transactions_objects.make_factoid_transactions_on_enterprisewallet(self.address,10)
        print result


    def test_send_factoid_transaction_in_enterprisewallet(self):
        result = self.entwallet_transactions_objects.send_factoid_transactions_on_enterprisewallet(self.address,10)
        print result
        time.sleep(2)
        result = self.entwallet_addressbook_objects.get_address(self.address)
        balance =  float(result['Content']['Balance'])
        balance_1 = self.factom_cli_create.check_waller_address_balance(self.address)
        self.assertTrue(float(balance) == float(balance_1), "Factoid balances on enterprise wallet and cli are not matching")


    def test_make_ec_transaction_in_enterprisewallet(self):
        result = self.entwallet_transactions_objects.make_factoid_transactions_on_enterprisewallet(self.ecaddress,10)
        print result


    def test_send_ec_transaction_in_enterprisewallet(self):
        result = self.entwallet_transactions_objects.send_factoid_transactions_on_enterprisewallet(self.ecaddress,10)
        print result
        time.sleep(3)
        result = self.entwallet_addressbook_objects.get_address(self.ecaddress)
        balance = result['Content']['Balance']
        balance_1 = self.factom_cli_create.check_waller_address_balance(self.ecaddress)
        self.assertTrue(float(balance) == float(balance_1),"Entry Credit balances  on enterprise wallet and cli are not matching")

