from enterprisewallet_objects.entwallet_transactions_objects import EnterpriseWalletTransactionsbjects
from enterprisewallet_objects.entwallet_addressbook_objects import EnterpriseWalletAddressBookObjects
from enterprisewallet_objects.entwallet_posttransaction import PostTransactionObjects
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
        self.posttransaction = PostTransactionObjects()
        self.factom_cli_create = FactomCliCreate()
        self.posttransaction = PostTransactionObjects()

        data = read_data_from_json('wallet_addresses.json')
        self.address = data['factoid_public_wallet_address']
        self.ecaddress = data['ec_public_wallet_address']
        self.outputaddress = data['fct_public_wallet_address_2']

    def test_list_alltransactions(self):
        result = self.entwallet_transactions_objects.get_transactions_from_enterprisewallet()
        print result

    def test_factoid_transaction_in_enterprisewallet(self):
        self.posttransaction.transtype = "factoid"
        self.posttransaction.outputaddresses = self.outputaddress
        self.posttransaction.outputamounts = 2
        result = self.entwallet_addressbook_objects.get_address(self.outputaddress)
        before_transaction_balance = float(result['Content']['Balance'])
        inputstring = self.posttransaction.make_inputparameter()
        self.entwallet_transactions_objects.make_transactions_on_enterprisewallet(inputstring)
        self.entwallet_transactions_objects.send_transactions_on_enterprisewallet(inputstring)
        time.sleep(3)
        result = self.entwallet_addressbook_objects.get_address(self.outputaddress)
        after_transaction_balance =  float(result['Content']['Balance'])
        balance = before_transaction_balance + self.posttransaction.outputamounts
        self.assertTrue(float(balance) == float(after_transaction_balance),"Transaction amount is not matching %s %s" % (balance, after_transaction_balance))

    def test_ec_transaction_in_enterprisewallet(self):
        self.posttransaction.transtype = "ec"
        self.posttransaction.outputaddresses = self.ecaddress
        self.posttransaction.outputamounts = 2
        inputstring = self.posttransaction.make_inputparameter()
        result = self.entwallet_addressbook_objects.get_address(self.ecaddress)
        before_transaction_balance = float(result['Content']['Balance'])
        self.entwallet_transactions_objects.make_transactions_on_enterprisewallet(inputstring)
        self.entwallet_transactions_objects.send_transactions_on_enterprisewallet(inputstring)
        time.sleep(3)
        result = self.entwallet_addressbook_objects.get_address(self.ecaddress)
        after_transaction_balance = result['Content']['Balance']
        balance = before_transaction_balance + self.posttransaction.outputamounts
        self.assertTrue(float(balance) == float(after_transaction_balance), "Transaction amount is not matching %s %s" % (
            balance, after_transaction_balance))

    def test_custom_transaction_in_enterprisewallet(self):
        self.posttransaction.transtype = "custom"
        self.posttransaction.outputaddresses = self.outputaddress
        self.posttransaction.outputamounts =  2
        self.posttransaction.inputaddresses =  self.address
        self.posttransaction.inputamounts = 2
        self.posttransaction.feeaddress = self.address
        result = self.entwallet_addressbook_objects.get_address(self.outputaddress)
        before_transaction_balance = float(result['Content']['Balance'])
        inputstring = self.posttransaction.make_inputparameter()
        self.entwallet_transactions_objects.make_transactions_on_enterprisewallet(inputstring)
        self.entwallet_transactions_objects.send_transactions_on_enterprisewallet(inputstring)
        time.sleep(5)
        result = self.entwallet_addressbook_objects.get_address(self.outputaddress)
        after_transaction_balance = float(result['Content']['Balance'])
        balance = before_transaction_balance + self.posttransaction.outputamounts
        self.assertTrue(float(balance) == float(after_transaction_balance), "Transaction amount is not matching %s %s" % (
            balance, after_transaction_balance))


    def test_get_needed_input(self):
        self.posttransaction.transtype = "factoid"
        self.posttransaction.outputaddresses = self.outputaddress
        self.posttransaction.outputamounts = 2
        inputstring = self.posttransaction.make_inputparameter()
        result = self.entwallet_transactions_objects.get_needed_input(inputstring)
        print result