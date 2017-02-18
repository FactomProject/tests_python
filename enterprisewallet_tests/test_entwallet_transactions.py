from enterprisewallet_objects.entwallet_transactions_objects import EnterpriseWalletTransactionsbjects
import unittest
from helpers.helpers import read_data_from_json

from nose.plugins.attrib import attr

@attr(fast=True)
class EnterpriseWalletTransactionTests(unittest.TestCase):

    def setUp(self):
        self.entwallet_transactions_objects = EnterpriseWalletTransactionsbjects()

    def test_list_alltransactions(self):
        result = self.entwallet_transactions_objects.get_transactions_from_enterprise()
        print result