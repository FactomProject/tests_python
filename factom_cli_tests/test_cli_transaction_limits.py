import unittest
import string
import random
import time

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class FactomCliTransactionLimits(unittest.TestCase):


    data = read_data_from_json('shared_test_data.json')

    ACK_WAIT_TIME = 10

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"' + self.data['words'] + '"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def test_transaction_limits_0(self):
        # attempt to add a 0 factoid input to a transaction
        balance1 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '0')
        self.assertTrue("Insufficient Fee" in self.factom_cli_create.sign_transaction_in_wallet(transaction_name))
        transaction_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(transaction_id, self.ACK_WAIT_TIME)
        balance2 = self.factom_cli_create.check_wallet_address_balance(self.first_address)

        self.assertTrue(balance1 == balance2, "Balance is subtracted on 0 factoids transaction")

    def test_add_minus_input_to_transaction(self):
        balance1 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '-1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.first_address, '-1')
        self.assertTrue("Insufficient Fee" in self.factom_cli_create.sign_transaction_in_wallet(transaction_name))
        transaction_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(transaction_id, self.ACK_WAIT_TIME)

        # balance should be unchanged
        balance2 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(balance1 == balance2, "Balance is subtracted for negative numbers")

    def test_add_too_small_input_to_transaction(self):
        balance1 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '0.0000000009')
        self.assertTrue("Insufficient Fee" in self.factom_cli_create.sign_transaction_in_wallet(transaction_name))
        transaction_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(transaction_id, self.ACK_WAIT_TIME)

        # test here balance after change
        balance2 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(balance1 == balance2, "Balance is subtracted for too small input")

    def test_add_more_than_balance_input_to_transaction(self):
        balance1 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        balance_plus_one = float(balance1.strip()) + 1
        transaction_fee = float(self.ecrate) * 9
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(balance_plus_one))
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.first_address, str(balance_plus_one - transaction_fee))
        self.assertIn("balance is too low", self.factom_cli_create.sign_transaction_in_wallet(transaction_name),
                      "Insufficient balance not detected")
        self.assertIn("Cannot send unsigned transaction", self.factom_cli_create.send_transaction(transaction_name), "Attempt to send unsigned transaction not detected")
        balance2 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(balance1 == balance2, "Balance is subtracted for too small input")

    def test_create_largest_allowable_transaction_10KB(self):
        """creating a large transaction

        a transaction with 78 inputs will take up 10KB
        so, 78 times:
        - a new factoid address is created (each input must come from a different address)
        - 1 factoid is transferred to this new address
        - an input from this new address is added to the master transaction
        the master transaction should still be signable at this point
        """

        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        for i in xrange(1, 79):
            new_name = transaction_name+str(i)
            self.add_input_to_master_transaction(transaction_name, new_name)
        self.assertNotIn("Transaction is greater than the max transaction size", self.factom_cli_create.sign_transaction_in_wallet(transaction_name), "Largest allowable transaction was not allowed")

        # now try to create a transaction >10KB by adding one more input to the master transaction
        new_name = transaction_name + '79'
        self.add_input_to_master_transaction(transaction_name, new_name)
        self.assertIn("Transaction is greater than the max transaction size", self.factom_cli_create.sign_transaction_in_wallet(transaction_name), "Too large transaction was allowed")

    def add_input_to_master_transaction(self, transaction_name, sub_transaction_name):
        temp_address = self.factom_cli_create.create_new_factoid_address()
        self.factom_cli_create.create_new_transaction_in_wallet(sub_transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(sub_transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(sub_transaction_name, temp_address, '1')
        self.factom_cli_create.set_account_to_subtract_fee_from_transaction_output(sub_transaction_name, temp_address)
        self.factom_cli_create.sign_transaction_in_wallet(sub_transaction_name)
        self.factom_cli_create.send_transaction_and_receive_transaction_id(sub_transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, temp_address,
                                                                          str(format(float(self.ecrate) * 2, 'f')))

