import unittest

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import create_random_string, read_data_from_json

@attr(fast=True)
class CLITestsTransactionLimits(unittest.TestCase):

    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        imported_addresses = self.cli_create.import_addresses(self.data['factoid_wallet_address'],
                                                              self.data['ec_wallet_address'])
        self.first_address = imported_addresses[0]
        self.entry_credit_address = imported_addresses[1]
        self.second_address = self.cli_create.create_new_factoid_address()
        words = '"' + self.data['words'] + '"'
        self.third_address = self.cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_creds_wallet2 = self.cli_create.create_entry_credit_address()

    def test_transaction_limits_0(self):
        # attempt to add a 0 factoid input to a transaction
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '0')
        self.assertIn("Insufficient Fee", self.cli_create.sign_transaction(transaction_name),
                        "0 input to transaction was allowed")
        self.assertIn("Cannot send unsigned transaction", self.cli_create.send_transaction(transaction_name), "Unsigned transaction sent")

    def test_add_minus_input_to_transaction(self):
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '-1')
        self.cli_create.add_output_to_transaction(transaction_name, self.first_address, '-1')
        self.assertIn("Insufficient Fee", self.cli_create.sign_transaction(transaction_name),
                        "Negative input to transaction was allowed")
        self.assertIn("Cannot send unsigned transaction", self.cli_create.send_transaction(transaction_name), "Unsigned transaction sent")

    def test_add_too_small_input_to_transaction(self):
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, self.ecrate)
        self.assertIn("Insufficient Fee", self.cli_create.sign_transaction(transaction_name),
                        "Input less than fee was allowed to transaction")
        self.assertIn("Cannot send unsigned transaction", self.cli_create.send_transaction(transaction_name), "Unsigned transaction sent")

    def test_add_more_than_balance_input_to_transaction(self):
        balance1 = self.cli_create.check_wallet_address_balance(self.first_address)
        balance_plus_one = float(balance1.strip()) + 1
        transaction_fee = float(self.ecrate) * 9
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, str(balance_plus_one))
        self.cli_create.add_output_to_transaction(transaction_name, self.first_address, str(balance_plus_one - transaction_fee))
        self.assertIn("balance is too low", self.cli_create.sign_transaction(transaction_name),
                      "Insufficient balance not detected")
        self.assertIn("Cannot send unsigned transaction", self.cli_create.send_transaction(transaction_name), "Attempt to send unsigned transaction not detected")

    def test_create_largest_allowable_transaction_10KB(self):
        '''
        creating a large transaction

        a transaction with 78 inputs will take up 10KB
        so, 78 times:
        - a new factoid address is created (each input must come from a different address)
        - 1 factoid is transferred to this new address
        - an input from this new address is added to the master transaction
        the master transaction should still be signable at this point
        '''
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        for i in xrange(1, 79):
            new_name = transaction_name+str(i)
            self.add_input_to_master_transaction(transaction_name, new_name)
        self.assertNotIn("Transaction is greater than the max transaction size", self.cli_create.sign_transaction(transaction_name), "Largest allowable transaction was not allowed")

        # now try to create a transaction >10KB by adding one more input to the master transaction
        new_name = transaction_name + '79'
        self.add_input_to_master_transaction(transaction_name, new_name)
        self.assertIn("Transaction is greater than the max transaction size", self.cli_create.sign_transaction(transaction_name), "Too large transaction was allowed")

    def add_input_to_master_transaction(self, transaction_name, sub_transaction_name):
        temp_address = self.cli_create.create_new_factoid_address()
        self.cli_create.create_new_transaction(sub_transaction_name)
        self.cli_create.add_input_to_transaction(sub_transaction_name, self.first_address, '1')
        self.cli_create.add_output_to_transaction(sub_transaction_name, temp_address, '1')
        self.cli_create.subtract_fee_from_transaction_output(sub_transaction_name, temp_address)
        self.cli_create.sign_transaction(sub_transaction_name)
        self.cli_create.send_transaction(sub_transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, temp_address,
                                                 str(format(float(self.ecrate) * 2, 'f')))

