import unittest
import os, binascii
import time

from nose.plugins.attrib import attr
from flaky import flaky

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from api_objects.factomd_api_objects import FactomApiObjects

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack

'''This bulk test checks for the rare occurrence of a chain being created and the server returning a server error
rather than a Chain ID.
Many chains are created because because the error is rare.
@attr(fast=False) because it takes a long time and shouldn't be run regularly'''

NUMBER_OF_RUNS = 5000

@attr(fast=False)
class FactomChainTests(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.factomd_api_objects = FactomApiObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(
            self.data['factoid_wallet_address'])
        self.entry_creds_wallet = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])

    def test_make_chain_and_check_balance(self):
        self.entry_creds_wallet = self.factom_cli_create.create_entry_credit_address()
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet, str(NUMBER_OF_RUNS * 12 ))
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        for i in range(NUMBER_OF_RUNS):
            print 'Chain', i + 1
            name_1 = create_random_string(5)
            name_2 = create_random_string(5)
            names_list = ['-n', name_1, '-n', name_2]
            self.assertFalse("looking for beginning of value" in self.factom_chain_object.make_chain_from_binary_file(self.entry_creds_wallet, path, names_list))
