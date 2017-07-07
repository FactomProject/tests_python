import unittest

from cli_objects.factom_cli_objects import FactomCliMainObjects
from helpers.helpers import read_data_from_json
from nose.plugins.attrib import attr

@attr(fast=True)
class FactomCliTransactionTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliMainObjects()

    '''The remote address feature of factomd is not currently activated
    def test_wallet_address_balance_remote(self):
        text = self.factom_cli_create.check_wallet_address_balance_remote('factom.michaeljbeam.me')
        self.assertTrue("fct" in text)
        self.assertTrue("ec" in text)'''

    def test_backup_wallet(self):
        self.assertTrue(len(self.factom_cli_create.backup_wallet().split(' ')) == 12, "12 words are not present in "
                                                                                      "wallet")
