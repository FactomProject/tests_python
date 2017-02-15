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

    def test_list_alltransactions(self):
        transactions = self.enterprisewallet.get_transactions_from_enterprise()
        print transactions

    def test_check_synched_status(self):
        result = self.enterprisewallet.get_synched_status()
        print result

    def test_address(self):
        result = self.enterprisewallet.get_address(self.address)
        print result

    def test_addresses(self):
        result = self.enterprisewallet.get_addresses()
        print result