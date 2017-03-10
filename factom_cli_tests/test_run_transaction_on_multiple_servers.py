import unittest
import os

from multiprocessing import Process
from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from api_objects.factomd_api_objects import FactomApiObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json, create_random_string

@attr(fast=True)
class FactomCliEndToEndTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    addresses = read_data_from_json('addresses.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"'+self.data['words']+'"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def test_create_multiple_same_transactions_on_different_nodes(self):
        cli_one = FactomCliCreate()
        cli_two = FactomCliCreate()
        cli_two.change_factomd_address(self.addresses['factomd_address_4'])
        cli_three = FactomCliCreate()
        cli_three.change_factomd_address(self.addresses['factomd_address_5'])
        cli_four = FactomCliCreate()
        cli_four.change_factomd_address(self.addresses['factomd_address_6'])

        cli_one.send_factoids(self.first_address, self.second_address, '200')
        third_address = self.factom_cli_create.create_new_factoid_address()

        for i in range(100):
            p1 = Process(
                target=self._send_factoid_transaction_on_cli_object(cli_one, self.second_address, third_address, '2'))
            p2 = Process(
                target=self._send_factoid_transaction_on_cli_object(cli_two, self.second_address, third_address, '2'))
            p3 = Process(
                target=self._send_factoid_transaction_on_cli_object(cli_three, self.second_address, third_address, '2'))
            p4 = Process(
                target=self._send_factoid_transaction_on_cli_object(cli_four, self.second_address, third_address, '2'))
            p1.start()
            p2.start()
            p3.start()
            p4.start()

        balance_after_1 = cli_one.check_wallet_address_balance(third_address)
        balance_after_2 = cli_two.check_wallet_address_balance(third_address)
        balance_after_3 = cli_three.check_wallet_address_balance(third_address)
        balance_after_4 = cli_four.check_wallet_address_balance(third_address)
        self.assertTrue(balance_after_1 == balance_after_2 and
                        balance_after_2 == balance_after_3 and balance_after_3 == balance_after_4,
                        'Balances are different')

    def test_compose_chain(self):
        factom_chain_object = FactomChainObjects()
        factomd_api_1 = FactomApiObjects()
        factomd_api_2 = FactomApiObjects()
        factomd_api_2.factomd_address = self.addresses['factomd_address_4']
        factomd_api_3 = FactomApiObjects()
        factomd_api_3.factomd_address = self.addresses['factomd_address_5']
        factomd_api_4 = FactomApiObjects()
        factomd_api_4.factomd_address = self.addresses['factomd_address_6']
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        text=''
        for i in range(100):
            text = factom_chain_object.compose_chain_from_binary_file(self.entry_creds_wallet1, path, name_1,
                                                                      name_2)
            start = text.find('"message":"') + 11
            end = text.find('"},"method', start)
            message = text[start:end]
            p1 = Process(
                target=self._send_chain_by_message(factomd_api_1, message))
            p2 = Process(
                target=self._send_chain_by_message(factomd_api_2, message))
            p3 = Process(
                target=self._send_chain_by_message(factomd_api_3, message))
            p4 = Process(
                target=self._send_chain_by_message(factomd_api_4, message))
            p1.start()
            p2.start()
            p3.start()
            p4.start()

        print text

    def _send_chain_by_message(self, api, message):
        text = api.commit_chain_by_message(message)


    def _send_factoid_transaction_on_cli_object(self, cli, address_from, address_to, amount):
        cli.send_factoids(address_from, address_to,  amount)



