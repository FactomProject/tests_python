from enterprisewallet_objects.entwallet_addressbook_objects import EnterpriseWalletAddressBookObjects
import unittest
from helpers.helpers import read_data_from_json

from nose.plugins.attrib import attr

@attr(fast=True)
class EnterpriseWalletAddressBookTests(unittest.TestCase):

    def setUp(self):
        self.entwallet_addressbook_objects = EnterpriseWalletAddressBookObjects()
        data = read_data_from_json('wallet_addresses.json')
        self.privatekey = data['factoid_wallet_address']
        self.address = data['factoid_public_wallet_address']
        self.deladdress = data['enterprise_wallet_address']
        self.koinifywords = data['words']
        self.externaladdress = data['external_address']


    def test_get_address(self):
        result = self.entwallet_addressbook_objects.get_address(self.address)
        print result

    def test_balance_of_all_addresses(self):
        result = self.entwallet_addressbook_objects.get_addresses()
        print result

    def test_get_address_only(self):
        result = self.entwallet_addressbook_objects.get_address_only()
        print result

    def test_get_balances(self):
        result = self.entwallet_addressbook_objects.get_balances()
        print result

    def test_check_change_address_name(self):
        name = "NameChange"
        result = self.entwallet_addressbook_objects.change_address_name(self.address,name)
        print result

    def test_delete_address(self):
        result = self.entwallet_addressbook_objects.delete_address(self.deladdress)
        print result

    def test_display_private_key(self):
        result = self.entwallet_addressbook_objects.display_private_key(self.address)
        print result

    def test_generate_new_factoid_address(self):
        name = "NEW-FCT-ADDRESS-01"
        result = self.entwallet_addressbook_objects.generate_new_factoid_address(name)
        print result

    def test_generate_new_ec_address(self):
        name = "NEW-EC-ADDRESS-01"
        result = self.entwallet_addressbook_objects.generate_new_entrycredit_address(name)
        print result

    def test_import_address_from_private_key(self):
        name = "IMPORT-ADDRESS-01"
        result = self.entwallet_addressbook_objects.import_address_private_key(name,self.privatekey)
        #payload = {"request": "new-address", "json": { 'Name' : self.name, 'Secret' : self.privatekey}}
        print result


    def test_import_koinify_address(self):
        name = "KOINIFY-ADDRESS"
        result = self.entwallet_addressbook_objects.import_koinify_address(name,self.koinifywords)
        print result


    def test_import_new_external_address(self):
        name = "EXTERNAL-ADDRESS-01"
        result = self.entwallet_addressbook_objects.import_new_external_address(name,self.externaladdress)
        print result

