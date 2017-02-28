import unittest
import os, binascii


from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
from nose.plugins.attrib import attr

@attr(fast=True)
class FactomCliTransactionTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()

    def test_backup_wallet(self):
        text = self.factom_cli_create.backup_wallet()
        self.assertTrue("Seed:" in text)
        self.assertTrue("kiwi" in text)
        self.assertTrue("Addresses:" in text)

