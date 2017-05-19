import unittest
import string
import random

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class FactomCliEndToEndTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"'+self.data['words']+'"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def test_allocate_funds_to_factoid_wallet_address_quiet_output(self):
        AMOUNT_SENT = 1
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                          str(AMOUNT_SENT))
        factom_flags_list = ['-q']

        # test add_output_to_transaction_quiet_flag
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, str(AMOUNT_SENT), flag_list=factom_flags_list)

        # check that output was added
        text = self.factom_cli_create.set_account_to_subtract_fee_from_transaction_output(transaction_name, self.second_address)
        transaction_dict = self.factom_chain_object.parse_full_transaction_data(text)
        self.assertEqual(str(AMOUNT_SENT - float(self.ecrate) * 12), transaction_dict['TotalOutputs'], "Quiet output not "
                                                                                         "accepted")
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)

        # compose transaction
        self.assertTrue('curl' and 'transaction' in self.factom_cli_create.compose_transaction(transaction_name), "Curl command not created")

        # send transaction
        text = self.factom_cli_create.send_transaction(transaction_name)
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        self.assertTrue(self.factom_cli_create.check_wallet_address_balance(self.second_address) is not 0, 'Factoids were not send to address: ' + self.second_address)

    def test_if_you_can_compose_wrong_transaction(self):
        self.assertTrue("Transaction name was not found" in self.factom_cli_create.compose_transaction('not_existing_trans'), 'Non-existent transaction was found in wallet')

    def test_request_balance_wrong_account(self):
        self.assertTrue('Undefined or invalid address' in self.factom_cli_create.check_wallet_address_balance(
            'Non-existent address'),'Non-existent address is showing up')

    def test_entry_credits_wallet(self):

        self.factom_cli_create.export_addresses()
        self.factom_cli_create.list_addresses()

        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        balance_2 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)

    def test_create_transaction_with_no_inputs_outputs_or_entry_creds(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.assertTrue('Insufficient Fee' in self.factom_cli_create.sign_transaction_in_wallet(transaction_name))
        self.assertTrue('Cannot send unsigned transaction' in self.factom_cli_create.send_transaction(transaction_name))

    def test_delete_transaction(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
        self.factom_cli_create.set_account_to_subtract_fee_from_transaction_output(transaction_name, self.second_address)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(), 'Transaction was not deleted')

    def test_create_transaction_with_not_equal_input_and_output(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.assertTrue("Inputs and outputs don't add up" in
                        self.factom_cli_create.set_account_to_subtract_fee_from_transaction_output(transaction_name, self.first_address
                                                                                                   ), "Input and output don't add up, but error is not displayed")
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')

    def test_add_input_larger_than_10_x_fee_to_correct_transaction_quiet_input(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)

        # test add_input_to_transaction_quiet_flag
        factom_flags_list = ['-q']
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1', flag_list=factom_flags_list)

        # check that input was added
        text = self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                               '1')
        transaction_dict = self.factom_chain_object.parse_full_transaction_data(text)
        self.assertEqual('1', transaction_dict['TotalInputs'], "Quiet input not accepted")

        self.factom_cli_create.set_account_to_subtract_fee_from_transaction_output(transaction_name, self.first_address)

        # try to overpay
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '10')
        self.assertTrue('Overpaying fee' in self.factom_cli_create.sign_transaction_in_wallet(transaction_name),
                        'Was able to overpay fee')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not removed')

    def test_create_transaction_with_no_output_or_ec(self):
        balance1 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(float(self.ecrate) * 8))
        self.factom_cli_create.set_account_to_add_fee_to_transaction_input(transaction_name, self.first_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        self.factom_cli_create.send_transaction(transaction_name)
        balance1_after = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(abs(float(balance1_after) - (float(balance1) - float(self.ecrate) * 8)) <= 0.001, 'Balance is not subtracted correctly')

    def test_create_transaction_with_input_to_ec_quiet_addfee(self):
        value_to_send = 1

        balance1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(value_to_send))
        self.factom_cli_create.add_entry_credit_output_to_transaction_in_wallet(transaction_name,
                                                                           self.entry_creds_wallet2, str(value_to_send))
        # test add_fee_to_transaction quiet flag
        factom_flags_list = ['-q']
        self.factom_cli_create.set_account_to_add_fee_to_transaction_input(transaction_name, self.first_address, flag_list=factom_flags_list)

        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        text = self.factom_cli_create.send_transaction(transaction_name)
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)
        ec_by_ec_to_factoids_rate = int(round(value_to_send / float(self.ecrate)))
        self.assertEqual(int(balance_1_after), int(balance1) + ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_create_transaction_with_input_to_output_and_ec(self):
        value_to_send = 2
        value_in_factoids_to_output = 1
        value_to_etc = 1
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                           str(value_to_send))
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, str(value_in_factoids_to_output))

        # check add_entry_credit_output_to_transaction quiet flag
        factom_flags_list = ['-q']
        self.factom_cli_create.add_entry_credit_output_to_transaction_in_wallet(transaction_name, self.entry_creds_wallet2,
                             str(value_to_etc), flag_list=factom_flags_list)
        self.assertTrue("Inputs and outputs don't add up" not in self.factom_cli_create.set_account_to_subtract_fee_from_transaction_output(transaction_name, self.second_address),
            "Entry credit output no added")
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)

        # check list_local_transactions Names flag
        factom_flags_list = ['-N']
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(flag_list=factom_flags_list), 'Transaction was not created locally in wallet')

        balance_1_before = int(self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2))
        text = self.factom_cli_create.send_transaction(transaction_name)
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_1_after = int(self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2))
        ec_by_ec_to_factoids_rate = int(round(int(balance_1) + value_to_etc / float(self.ecrate)))
        self.assertEqual(balance_1_after, ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_buy_entry_creds(self):
        value_of_etc = 150
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        text = self.factom_cli_create.force_buy_ec(self.first_address, self.entry_creds_wallet1, str(value_of_etc))
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        self. assertEqual(int(balance_1_after), int(balance_1) + value_of_etc, 'EC were not bought')

    def test_buy_entry_credits_with_wrong_accounts(self):
        value_of_etc = 150
        self.assertTrue('not a Factoid' in self.factom_cli_create.force_buy_ec('wrong_address', self.entry_creds_wallet1, str(value_of_etc)))
        self.assertTrue('not an Entry' in self.factom_cli_create.force_buy_ec(self.first_address, 'wrong_address', str(value_of_etc)))

    def test_send_factoids(self):
        value_of_factoids = 1
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.second_address)
        text = self.factom_cli_create.send_factoids(self.first_address, self.second_address, str(value_of_factoids))
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.second_address)
        self.assertEqual(int(balance_1_after), int(balance_1) + value_of_factoids)

    def test_for_sof_425(self):
        # rounding error may cause internal error when amount sent is very close to available balance
        second_address = self.factom_cli_create.create_new_factoid_address()
        third_address = self.factom_cli_create.create_new_factoid_address()
        text = self.factom_cli_create.send_factoids(self.first_address, second_address, '100')
        chain_dict = self.factom_chain_object.parse_summary_transaction_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)

        self.assertTrue('100' in self.factom_cli_create.check_wallet_address_balance(second_address))
        self.assertTrue('balance is too low' in self.factom_cli_create.send_factoids(second_address, third_address, '99.9999'))
        self.assertTrue('0' in self.factom_cli_create.check_wallet_address_balance(third_address))
        self.factom_cli_create.send_factoids(second_address, third_address, '99.99988')
        self.assertTrue('99.99988' in self.factom_cli_create.check_wallet_address_balance(third_address))
