import unittest
import string
import random
import time

from api_objects.factom_cli_create import FactomCliCreate

class FactomCliEndToEndTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factom_cli_create = FactomCliCreate()
        cls.first_address = cls.factom_cli_create.import_address_from_factoid("Fs2DNirmGDtnAZGXqca3XHkukTNMxoMGFFQxJA3bAjJnKzzsZBMH") #TODO data pachage for that
        cls.second_address = cls.factom_cli_create.create_new_factoid_address()
        words = '"salute umbrella proud setup delay ginger practice split toss jewel tuition stool"'
        cls.third_address = cls.factom_cli_create.import_words_from_koinify_into_wallet(words)
        cls.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()

    def test_alocate_founds_to_factoid_walled_address(self):

        balance1 = self.factom_cli_create.check_waller_address_balance(self.first_address)
        balance2 = self.factom_cli_create.check_waller_address_balance(self.second_address)
        balance3 = self.factom_cli_create.check_waller_address_balance(self.third_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_foactoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
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
        entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid('Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

        self.factom_cli_create.export_addresses()
        self.factom_cli_create.list_adresses()

        balance_1 = self.factom_cli_create.check_waller_address_balance(entry_creds_wallet1)
        balance_2 = self.factom_cli_create.check_waller_address_balance(entry_creds_wallet2)

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
        self.factom_cli_create.add_foactoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
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
        self.factom_cli_create.add_foactoid_output_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.first_address)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '10')
        self.assertTrue('Overpaying Fee' in self.factom_cli_create.sign_transaction_in_wallet(transaction_name),
                        'Was able to overpay fee')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertTrue(transaction_name not in self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')







    def _wait_for_ack(self, transaction_id, time_to_wait):
        status = 'not found'
        i = 0
        while "not found" in status and i < time_to_wait:
            status = self.factom_cli_create.request_transaction_acknowledgement(transaction_id)
            time.sleep(1)
            i += 1

