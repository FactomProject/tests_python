import unittest
import string
import random
import time

from api_objects.factom_cli_create import FactomCliCreate

class FactomCliEndToEndTest(unittest.TestCase):

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.first_address = self.factom_cli_create.import_address_from_factoid("Fs2DNirmGDtnAZGXqca3XHkukTNMxoMGFFQxJA3bAjJnKzzsZBMH") #TODO data pachage for that
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"salute umbrella proud setup delay ginger practice split toss jewel tuition stool"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            'Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def test_alocate_founds_to_factoid_walled_address(self):

        balance1 = self.factom_cli_create.check_waller_address_balance(self.first_address)
        balance2 = self.factom_cli_create.check_waller_address_balance(self.second_address)
        balance3 = self.factom_cli_create.check_waller_address_balance(self.third_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.second_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        #compose transaction
        transaction_hash =  self.factom_cli_create.compose_transactsion_and_return_transactoin_code(transaction_name)
        self.assertFalse('Internal error: Transaction not found' in self.factom_cli_create.request_transaction_acknowledgement(transaction_hash), "Transaction is not found in system")
        transaction_id = self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)
        self._wait_for_ack(transaction_id, 60)

        #test here balance after change
        balance1_after = self.factom_cli_create.check_waller_address_balance(self.first_address)
        balance2_after = self.factom_cli_create.check_waller_address_balance(self.second_address)
        balance3_after = self.factom_cli_create.check_waller_address_balance(self.third_address)


        self.assertTrue(balance2_after is not 0, 'cash was not send to address: ' + self.second_address)

    def test_if_you_can_compose_wrong_transaction(self):
        self.assertTrue("Transaction name was not found" in self.factom_cli_create.compose_transactsion('not_egsisting_trans'), 'Not existing transaction was found in wallet')

    def test_request_balace_wring_account(self):
        self.assertTrue('Undefined' in self.factom_cli_create.check_waller_address_balance('wrong_account'))

    def test_entry_credits_wallet(self):

        self.factom_cli_create.export_addresses()
        self.factom_cli_create.list_adresses()

        balance_1 = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet1)
        balance_2 = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet2)

        #TODO think about assertion


    def test_create_transaction_with_no_inputs_outputs_and_entry_creds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.second_address)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(), 'Transaction was not deleted')

    def test_create_transaction_with_not_equal_input_and_output(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.assertTrue("Inputs and outputs don't add up" in
                        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.first_address
                                                                                                  ), "Input and outpt are don't adding up, but errior is not displayed")
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')

    def test_add_input_larger_than_10_x_fee_to_correct_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.first_address)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '10')
        self.assertTrue('Overpaying Fee' in self.factom_cli_create.sign_transaction_in_wallet(transaction_name),
                        'Was able to overpay fee')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')

    def test_create_transaction_with_no_output_or_ec(self):
        balance1 = self.factom_cli_create.check_waller_address_balance(self.first_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(float(self.ecrate) * 8))
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        transaction_id = self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)
        self._wait_for_ack(transaction_id, 60)
        balance1_after = self.factom_cli_create.check_waller_address_balance(self.first_address)
        self.assertTrue(abs(float(balance1_after) - (float(balance1) - float(self.ecrate) * 8)) <= 0.001, 'Balance is not substracted '
                                                                                             'correctly')

    def test_create_transaction_with_input_to_ec(self):
        value_to_send = 1

        balance1 = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet2)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, str(value_to_send))

        self.factom_cli_create.add_entry_credit_output_to_transaction_in_wallet(transaction_name,
                                                                           self.entry_creds_wallet2, str(value_to_send))
        self.factom_cli_create.set_acconut_to_add_fee_from_transaction_input(transaction_name, self.first_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        transaction_id = self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)
        self._wait_for_ack(transaction_id, 60)
        balance_1_after = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet2)
        ec_by_ec_to_factoids_rate = int(round(value_to_send / float(self.ecrate)))
        self.assertEqual(int(balance_1_after), int(balance1) + ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_create_transaction_with_input_to_output_and_ec(self):
        value_to_send = 2
        value_in_factoids_to_output = 1
        value_to_etc = 1
        balance_1 = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet2)

        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address,
                                                                           str(value_to_send))
        self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, str(value_in_factoids_to_output))

        self.factom_cli_create.add_entry_credit_output_to_transaction_in_wallet(transaction_name,
                                                                                self.entry_creds_wallet2,
                                                                                str(value_to_etc))
        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.second_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        self.assertTrue(transaction_name in self.factom_cli_create.list_local_transactions(), 'Transaction was created')

        transaction_id = self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)
        self._wait_for_ack(transaction_id, 60)
        balance_1_after = int(self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet2))

        ec_by_ec_to_factoids_rate = int(round(int(balance_1) + value_to_etc / float(self.ecrate)))
        print balance_1
        print balance_1_after
        print ec_by_ec_to_factoids_rate
        self.assertEqual(balance_1_after, ec_by_ec_to_factoids_rate, 'Wrong output of transaction')

    def test_buy_entry_creds(self):
        value_of_etc = 150
        balance_1 = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet1)
        transaction_id = self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet1, str(value_of_etc))
        self._wait_for_ack(transaction_id, 60)
        balance_1_after = self.factom_cli_create.check_waller_address_balance(self.entry_creds_wallet1)
        self. assertEqual(int(balance_1_after), int(balance_1) + value_of_etc, 'EC were not bought')

    def test_buy_entry_credits_with_wrong_accounts(self):
        value_of_etc = 150
        self.assertTrue('not a Factoid' in self.factom_cli_create.buy_ec('wrong_address', self.entry_creds_wallet1, str(value_of_etc)))
        self.assertTrue('not an Entry' in self.factom_cli_create.buy_ec(self.first_address, 'wrong_address', str(value_of_etc)))

    def test_send_factoids(self):
        value_of_factoids = 1
        balance_1 = self.factom_cli_create.check_waller_address_balance(self.second_address)
        transaction_id = self.factom_cli_create.send_factoids(self.first_address, self.second_address, str(value_of_factoids))
        self._wait_for_ack(transaction_id, 60)
        balance_1_after = self.factom_cli_create.check_waller_address_balance(self.second_address)
        self.assertEqual(int(balance_1_after), int(balance_1) + value_of_factoids)



    def _wait_for_ack(self, transaction_id, time_to_wait):
        status = 'not found'
        i = 0
        while "TransactionACK" not in status and i < time_to_wait:
            status = self.factom_cli_create.request_transaction_acknowledgement(transaction_id)
            time.sleep(1)
            i += 1

