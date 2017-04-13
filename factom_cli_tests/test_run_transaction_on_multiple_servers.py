import unittest
from multiprocessing import Process

from nose.plugins.attrib import attr
from flaky import flaky

from cli_objects.factom_cli_create import FactomCliCreate
from helpers.helpers import read_data_from_json

@flaky(max_runs=3, min_passes=1)
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


    def notest_create_multiple_same_transactions_on_different_nodes(self):
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


    def _send_factoid_transaction_on_cli_object(self, cli, address_from, address_to, amount):
        cli.send_factoids(address_from, address_to,  amount)