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
        text = self.factom_cli_create.check_wallet_address_balance_remote('factom.michaeljbeam.me')
        self.assertTrue("fct" in text)
        self.assertTrue("ec" in text)

    def test_backup_wallet(self):
        text = self.factom_cli_create.backup_wallet()
        self.assertTrue("Seed:" in text)
        self.assertTrue("kiwi" in text)
        self.assertTrue("Addresses:" in text)

