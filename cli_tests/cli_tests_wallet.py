import unittest

from nose.plugins.attrib import attr
from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers.helpers import read_data_from_json

@attr(fast=True)
class CLITestsWallet(unittest.TestCase):
    cli_create = CLIObjectsCreate()
    cli_objects = CLIObjectsChain()
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        pass
    '''
    The remote address feature of factomd is not currently activated
    def test_wallet_address_balance_remote(self):
        text = self.cli_create.check_wallet_address_balance_remote('factom.michaeljbeam.me')
        self.assertTrue("fct" in text)
        self.assertTrue("ec" in text)
    '''
    def test_backup_wallet(self):
        self.assertTrue(len(self.cli_create.backup_wallet().split(' ')) == 12, "12 words are not present in wallet")

    def test_balance_totals(self):
        result = self.cli_create.check_wallet_address_balancetotals()
        balance_total = self.cli_objects.parse_balance_totals(result)
        self.assertEqual(balance_total['savedFCT'],balance_total['ackFCT'],"saved FCT not equal to ack FCT")
        self.assertEqual(balance_total['savedEC'], balance_total['ackEC'], "saved EC not equal to ack EC")

    def test_various_flags_balance_totals(self):
        result = self.cli_create.check_wallet_address_balancetotals()
        balance_total = self.cli_objects.parse_balance_totals(result)
        balance_FS = self.cli_create.check_wallet_address_balancetotals_with_flags("-FS")
        balance_FA = self.cli_create.check_wallet_address_balancetotals_with_flags("-FA")
        balance_ES = self.cli_create.check_wallet_address_balancetotals_with_flags("-ES")
        balance_EA = self.cli_create.check_wallet_address_balancetotals_with_flags("-EA")
        self.assertEqual(balance_total['savedFCT'],balance_FS,"saved FCT is not matching")
        self.assertEqual(balance_total['ackFCT'], balance_FA, "ack FCT is not matching")
        self.assertEqual(balance_total['savedEC'], balance_ES, "saved EC is not matching")
        self.assertEqual(balance_total['ackEC'], balance_EA, "ack EC is not matching")
        self.assertEqual(balance_FS, balance_FA, "saved FCT is not matching")
        self.assertEqual(balance_FS, balance_FA, "ack FCT is not matching")
        print(result)

