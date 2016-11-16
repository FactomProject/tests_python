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

    def test_factom_ecrate(self):
        #do we have ability to know entry credit convention rate before test?
        ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.assertEqual(ecrate.strip(), '0.006666', "Ecrate is not as expected and is value is: " + ecrate)

    def test_alocate_founds_to_factoid_walled_address(self):

        balance1 = self.factom_cli_create.check_waller_address_balance(self.first_address)
        balance2 = self.factom_cli_create.check_waller_address_balance(self.second_address)
        balance3 = self.factom_cli_create.check_waller_address_balance(self.third_address)
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '150')
        self.factom_cli_create.add_foactoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '150')
        self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.second_address)
        self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        #compose transaction
        transaction_hash =  self.factom_cli_create.compose_transactsion_and_return_transactoin_code(transaction_name)
        self.assertFalse('Internal error: Transaction not found' in self.factom_cli_create.request_transaction_acknowledgement(transaction_hash), "Transaction is not found in system")
        transaction_id = self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)

        #TODO uncomment when you have amount to send/you will cnow
        #self._wait_for_ack()

        #test here balance after change
        balance1_after = self.factom_cli_create.check_waller_address_balance(self.first_address)
        balance2_after = self.factom_cli_create.check_waller_address_balance(self.second_address)
        balance3_after = self.factom_cli_create.check_waller_address_balance(self.third_address)

        self.assertEquals(int(balance2) + 150, balance2_after, 'cash was not send to address: ' + self.second_address)

    def test_if_you_can_compose_wrong_transaction(self):
        self.assertTrue("Transaction name was not found" in self.factom_cli_create.compose_transactsion('not_egsisting_trans'), 'Not existing transaction was found in wallet')

    def test_request_balace_wring_account(self):
        self.assertTrue('Undefined' in self.factom_cli_create.check_waller_address_balance('wrong_account'))

    def test_entry_credits_wallet(self):
        entry_creds_wallet1 = self.factom_cli_create.factom_importaddress('Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

        balance_1 = self.factom_cli_create.check_waller_address_balance(entry_creds_wallet1)
        balance_2 = self.factom_cli_create.check_waller_address_balance(entry_creds_wallet2)

        #TODO think about assertion

    def create_transaction_with_no_inputs_outputs_and_entry_creds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        print self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)

    def _wait_for_ack(self, transaction_id, time_to_wait):
        status = ''
        i = 0
        while "not found" in status and i < time_to_wait:
            status = self.factom_cli_create.request_transaction_acknowledgement(transaction_id)
            time.sleep(1)
            i += 1

