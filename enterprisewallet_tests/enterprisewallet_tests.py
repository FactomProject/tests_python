from enterprisewallet_objects.factom_enterprisewallet_objects import EnterpriseWalletObjects
import unittest
from helpers.helpers import read_data_from_json

from nose.plugins.attrib import attr

@attr(fast=True)
class FactomEnterpriseWalletTests(unittest.TestCase):

    def setUp(self):
        self.enterprisewallet = EnterpriseWalletObjects()
        data = read_data_from_json('shared_test_data.json')
        self.address = data['factoid_public_wallet_address']
        self.deladdress = data['enterprise_wallet_address']

    def test_get_status_enterprise_wallet(self):
        result = self.enterprisewallet.get_status_enterprise_wallet()
        print result

    def test_list_alltransactions(self):
        result = self.enterprisewallet.get_transactions_from_enterprise()
        print result

    def test_check_synched_status(self):
        result = self.enterprisewallet.get_synched_status()
        print result

    def test_get_address(self):
        result = self.enterprisewallet.get_address(self.address)
        print result

    def test_balance_of_all_addresses(self):
        result = self.enterprisewallet.get_addresses()
        print result

    def test_get_address_only(self):
        result = self.enterprisewallet.get_address_only()
        print result

    def test_get_balances(self):
        result = self.enterprisewallet.get_balances()
        print result

    def test_check_change_address_name(self):
        name = "NameChange"
        result = self.enterprisewallet.change_address_name(self.address,name)
        print result

    def test_delete_address(self):
        result = self.enterprisewallet.delete_address(self.deladdress)
        print result

    def test_display_private_key(self):
        result = self.enterprisewallet.display_private_key(self.address)
        print result

    def test_generate_new_factoid_address(self):
        name = "NEW-FCT-ADDRESS-01"
        result = self.enterprisewallet.generate_new_factoid_address(name)
        print result

    def test_generate_new_ec_address(self):
        name = "NEW-EC-ADDRESS-01"
        result = self.enterprisewallet.generate_new_entrycredit_address(name)
        print result