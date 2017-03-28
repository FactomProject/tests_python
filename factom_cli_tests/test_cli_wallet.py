import unittest

from cli_objects.factom_cli_create import FactomCliCreate
from helpers.helpers import read_data_from_json
from nose.plugins.attrib import attr

@attr(fast=True)
class FactomCliTransactionTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()

    def test_wallet_address_balance_remote(self):
        text = self.factom_cli_create.check_wallet_address_balance_remote()
        self.assertTrue("Wallet Name Lookup is Insecure" == text, "Remote address does not exist")
        self.assertTrue("fct" in text, "Remote factoid wallet is not present")
        self.assertTrue("ec" in text, "Remote ec wallet is not present")

    def test_backup_wallet(self):
        text = self.factom_cli_create.backup_wallet()
        self.assertTrue("Seed:" in text, "Seed not reported")
        self.assertTrue("Addresses:" in text, "Addresses not reported")

