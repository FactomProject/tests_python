import unittest
import string
import random
import time
from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class FactomCliEndToEndTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    ACK_WAIT_TIME = 20

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

    def test_allocate_funds_to_factoid_wallet_address(self):

        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
        self.factom_cli_create.set_account_to_subtract_fee_from_that_transaction(transaction_name, self.second_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        # compose transaction
        transaction_hash = self.factom_cli_create.compose_transaction_and_return_transaction_code(transaction_name)
        self.assertFalse(
            'Internal error: Transaction not found' in self.factom_cli_create.request_transaction_acknowledgement(
                transaction_hash), "Transaction is not found in system")
        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance2_after = self.factom_cli_create.check_wallet_address_balance(self.second_address)

        self.assertTrue(balance2_after is not 0, 'cash was not send to address: ' + self.second_address)

    def test_if_you_can_compose_wrong_transaction(self):
        self.assertTrue("Transaction name was not found" in self.factom_cli_create.compose_transaction('not_existing_trans'), 'Not existing transaction was found in wallet')

    def test_request_balance_wrong_account(self):
        self.assertTrue('Undefined' in self.factom_cli_create.check_wallet_address_balance('wrong_account'))

    def test_entry_credits_wallet(self):

        self.factom_cli_create.export_addresses()
        self.factom_cli_create.list_addresses()

        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        balance_2 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)


    def test_create_transaction_with_no_inputs_outputs_and_entry_creds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue('Cannot send unsigned transaction' in self.factom_cli_create.send_transaction(transaction_name))

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
        self.factom_cli_create.set_account_to_subtract_fee_from_that_transaction(transaction_name, self.second_address)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(), 'Transaction was not deleted')

    def test_create_transaction_with_not_equal_input_and_output(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.assertTrue("Inputs and outputs don't add up" in
                        self.factom_cli_create.set_account_to_subtract_fee_from_that_transaction(transaction_name, self.first_address
                                                                                                  ), "Input and output are not adding up, but error is not displayed")
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')

    def test_add_input_larger_than_10_x_fee_to_correct_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.set_account_to_subtract_fee_from_that_transaction(transaction_name, self.first_address)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '10')
        self.assertTrue('Overpaying fee' in self.factom_cli_create.sign_transaction_in_wallet(transaction_name),
                        'Was able to overpay fee')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')

    def test_create_transaction_with_no_output_or_ec(self):
        balance1 = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(float(self.ecrate) * 8))
        self.factom_cli_create.quiet_set_account_to_add_fee_from_transaction_input(transaction_name,self.first_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance1_after = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(abs(float(balance1_after) - (float(balance1) - float(self.ecrate) * 8)) <= 0.001, 'Balance is not subtracted correctly')

    def test_create_transaction_with_input_to_ec(self):
        value_to_send = 1

        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(value_to_send))

        self.factom_cli_create.add_entry_credit_output_to_transaction_in_wallet(transaction_name,
                                                                           self.entry_creds_wallet2, str(value_to_send))
        self.factom_cli_create.set_account_to_add_fee_from_transaction_input(transaction_name, self.first_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)
        ec_by_ec_to_factoids_rate = int(round(value_to_send / float(self.ecrate)))
        self.assertEqual(int(balance_1_after), int(balance_1) + ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_create_transaction_with_input_to_remote_ec(self):
        value_to_send = 1

        balance_1 = self.factom_cli_create.check_wallet_address_balance_remote()
        self.assertTrue("Wallet Name Lookup is Insecure" == balance_1, "Remote address does not exist")
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(value_to_send))

        self.factom_cli_create.add_entry_credit_output_to_transaction_remote(transaction_name, str(value_to_send))
        self.factom_cli_create.set_account_to_add_fee_from_transaction_input(transaction_name, self.first_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        # ****change this to extract ec balance after remote address is reregistered at Netki
        balance_1_after = self.factom_cli_create.check_wallet_address_balance_remote()
        self.assertTrue("Wallet Name Lookup is Insecure" == balance_1, "Remote address does not exist")
        # ***************************************
        ec_by_ec_to_factoids_rate = int(round(value_to_send / float(self.ecrate)))
        self.assertEqual(int(balance_1_after), int(balance_1) + ec_by_ec_to_factoids_rate, 'Wrong output of transaction'    )

    def test_create_transaction_with_input_to_output_and_ec(self):
        value_to_send = 2
        value_in_factoids_to_output = 1
        value_to_etc = 1

        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)

        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                           str(value_to_send))
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, str(value_in_factoids_to_output))

        self.factom_cli_create.add_entry_credit_output_to_transaction_in_wallet(transaction_name,
                                                                                self.entry_creds_wallet2,
                                                                                str(value_to_etc))
        self.factom_cli_create.set_account_to_subtract_fee_from_that_transaction(transaction_name, self.second_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = int(self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2))

        ec_by_ec_to_factoids_rate = int(round(int(balance_1) + value_to_etc / float(self.ecrate)))
        self.assertEqual(balance_1_after, ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_quiet_create_transaction_with_input_to_output_and_ec(self):
        value_to_send = 2
        value_in_factoids_to_output = 1
        value_to_etc = 1

        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2)

        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.quiet_create_new_transaction_in_wallet(transaction_name)

        self.factom_cli_create.quiet_add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                           str(value_to_send))
        self.factom_cli_create.quiet_add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, str(value_in_factoids_to_output))
        self.factom_cli_create.quiet_add_entry_credit_output_to_transaction_in_wallet(transaction_name,
                                                                                self.entry_creds_wallet2,
                                                                                str(value_to_etc))

        self.factom_cli_create.quiet_set_account_to_subtract_fee_from_that_transaction(transaction_name,
                                                                                   self.second_address)
        self.factom_cli_create.quiet_sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = int(self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet2))

        ec_by_ec_to_factoids_rate = int(round(int(balance_1) + value_to_etc / float(self.ecrate)))
        self.assertEqual(balance_1_after, ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_create_transaction_with_input_to_output_and_ec_remote(self):
        value_to_send = 2
        value_in_factoids_to_output = 1
        value_to_etc = 1

        balance_1 = self.factom_cli_create.check_wallet_address_balance_remote()
        self.assertTrue("Wallet Name Lookup is Insecure" == balance_1, "Remote address does not exist")

        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                          str(value_to_send))
        self.factom_cli_create.add_factoid_output_to_transaction_remote(transaction_name, self.second_address,
                                                                           str(value_in_factoids_to_output))

        self.factom_cli_create.add_entry_credit_output_to_transaction_remote(transaction_name,
                                                                                self.entry_creds_wallet2,
                                                                                str(value_to_etc))
        self.factom_cli_create.set_account_to_add_fee_from_transaction_input(transaction_name, self.first_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        tx_id = self.factom_cli_create.send_transaction_and_receive_transaction_id(transaction_name)
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = int(self.factom_cli_create.check_wallet_address_balance_remote(self.entry_creds_wallet2))

        ec_by_ec_to_factoids_rate = int(round(int(balance_1) + value_to_etc / float(self.ecrate)))
        self.assertEqual(balance_1_after, ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_buy_entry_creds(self):
        value_of_etc = 150
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        text = self.factom_cli_create.force_buy_ec(self.first_address, self.entry_creds_wallet1, str(value_of_etc))
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        self. assertEqual(int(balance_1_after), int(balance_1) + value_of_etc, 'EC were not bought')

        # quiet buy entry credits
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        self.factom_cli_create.quiet_buy_ec(self.first_address, self.entry_creds_wallet1, str(value_of_etc))
        time.sleep(self.ACK_WAIT_TIME)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        self.assertEqual(int(balance_1_after), int(balance_1) + value_of_etc, 'EC were not bought')

        # remote buy entry credits
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        # self.assertTrue("Wallet Name Lookup is Insecure" == balance_1, "Remote address does not exist")
        text = self.factom_cli_create.buy_ec_remote(self.first_address, str(value_of_etc))
        '''
        # REPLACE THIS CODE WHEN NETKI ADDRESS IS REINSTATED
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        self.assertEqual(int(balance_1_after), int(balance_1) + value_of_etc, 'EC were not bought')
        '''
        # buy entry credits and return tx_id
        balance_1 = self.factom_cli_create.check_wallet_address_balance(self.entry_creds_wallet1)
        tx_id = self.factom_cli_create.buy_ec_return_tx_id(self.first_address, self.entry_creds_wallet1, str(value_of_etc))
        # any error message will contain a capital letter
        self.assertTrue(not any(map(str.isupper, tx_id)), "tx_id not returned")
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
        chain_dict = self.factom_chain_object.parse_chain_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id, self.ACK_WAIT_TIME)
        balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.second_address)
        self.assertEqual(int(balance_1_after), int(balance_1) + value_of_factoids)

    def test_for_sof_425(self):
        # todo change assert when fixed
        second_address = self.factom_cli_create.create_new_factoid_address()
        third_address = self.factom_cli_create.create_new_factoid_address()
        self.factom_cli_create.send_factoids(self.first_address, second_address, '100')


        self.assertTrue('100' in self.factom_cli_create.check_wallet_address_balance(second_address))
        self.assertTrue('balance is too low' in self.factom_cli_create.send_factoids(second_address, third_address, '99.9999'))
        self.assertTrue('0' in self.factom_cli_create.check_wallet_address_balance(third_address))
        self.factom_cli_create.send_factoids(second_address, third_address, '99.99988')
        self.assertTrue('99.99988' in self.factom_cli_create.check_wallet_address_balance(third_address))
