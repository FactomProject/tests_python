import unittest

from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import read_data_from_json
from nose.plugins.attrib import attr

@attr(fast=True)
class CLITestsWallet(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
    '''
    The remote address feature of factomd is not currently activated
    def test_wallet_address_balance_remote(self):
        text = self.cli_create.check_wallet_address_balance_remote('factom.michaeljbeam.me')
        self.assertTrue("fct" in text)
        self.assertTrue("ec" in text)
    '''
    def test_backup_wallet(self):
        self.assertTrue(len(self.cli_create.backup_wallet().split(' ')) == 12, "12 words are not present in wallet")
