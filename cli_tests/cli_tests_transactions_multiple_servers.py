import unittest


from nose.plugins.attrib import attr
from cli_objects.cli_objects_create import CLIObjectsCreate
from multiprocessing import Process
from helpers.helpers import read_data_from_json

@attr(last=True)
class CLITestsTransactionsMultipleServers(unittest.TestCase):
    cli_create = CLIObjectsCreate()
    data = read_data_from_json('shared_test_data.json')
    server_addresses = read_data_from_json('addresses.json')

    def setUp(self):
        imported_addresses = self.cli_create.import_addresses(self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        self.first_address = imported_addresses[0]
        self.entry_credit_address = imported_addresses[1]
        self.second_address = self.cli_create.create_new_factoid_address()
        words = '"'+self.data['words']+'"'
        self.third_address = self.cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_creds_wallet2 = self.cli_create.create_entry_credit_address()

    def test_create_multiple_same_transactions_on_different_nodes(self):
        cli_one = CLIObjectsCreate()
        cli_two = CLIObjectsCreate()
        cli_two.change_factomd_address(self.server_addresses['factomd_address_4'])
        cli_three = CLIObjectsCreate()
        cli_three.change_factomd_address(self.server_addresses['factomd_address_5'])
        cli_four = CLIObjectsCreate()
        cli_four.change_factomd_address(self.server_addresses['factomd_address_3'])
        cli_one.send_factoids(self.first_address, self.second_address, '200')
        third_address = self.cli_create.create_new_factoid_address()

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
                        'Balances are different Balance_1: ' + str(balance_after_1) + ' balance_2: ' +
                        str(balance_after_2) + ' balance_3 ' + str(balance_after_3) + ' balance_4 ' +
                        str(balance_after_4))


    def _send_factoid_transaction_on_cli_object(self, cli, address_from, address_to, amount):
        cli.send_factoids(address_from, address_to,  amount)
