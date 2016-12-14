import unittest
import string
import random
import time

from api_objects.factom_wallet_api_objects import FactomWalletApiObjects
from api_objects.factomd_api_objects import FactomApiObjects

class FactomWalletApiTest(unittest.TestCase):


    def setUp(self):
        self.wallet_api_objects = FactomWalletApiObjects()
        self.factomd_api_objects = FactomApiObjects()
        self.first_address = self.wallet_api_objects.import_addres_by_secret("Fs2DNirmGDtnAZGXqca3XHkukTNMxoMGFFQxJA3bAjJnKzzsZBMH")
        self.second_address = self.wallet_api_objects.generate_factoid_address()
        words = "salute umbrella proud setup delay ginger practice split toss jewel tuition stool"
        #self.third_address = self.wallet_api_objects.import_mnemonic(words)
        #print self.third_address
        self.ecrate = self.factomd_api_objects.get_entry_credits_rate()
        print self.ecrate
        self.entry_creds_wallet2 = self.wallet_api_objects.import_addres_by_secret('Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        self.entry_creds_wallet2 = self.wallet_api_objects.generate_ec_address()

    def test_alocate_founds_to_factoid_walled_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        print self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, '1')
        self.wallet_api_objects.add_factoid_output_to_transaction(transaction_name, self.second_address, '1')
        self.wallet_api_objects.substract_fee_in_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        print self.wallet_api_objects.compose_transaction(transaction_name)



        # self.factom_cli_create.create_new_transaction_in_wallet(transaction_name)
        # self.factom_cli_create.add_foactoid_input_to_transaction_in_wallet(transaction_name, self.first_address, '1')
        # self.factom_cli_create.add_factoid_output_to_transaction_in_wallet(transaction_name, self.second_address, '1')
        # self.factom_cli_create.set_account_to_substract_fee_from_that_transaction(transaction_name, self.second_address)
        # self.factom_cli_create.sign_transaction_in_wallet(transaction_name)
        # #compose transaction
        # transaction_hash =  self.factom_cli_create.compose_transactsion_and_return_transactoin_code(transaction_name)
        # self.assertFalse('Internal error: Transaction not found' in self.factom_cli_create.request_transaction_acknowledgement(transaction_hash), "Transaction is not found in system")
        # transaction_id = self.factom_cli_create.send_transaction_and_recive_transaction_id(transaction_name)
        # self._wait_for_ack(transaction_id, 60)
        # balance2_after = self.factom_cli_create.check_waller_address_balance(self.second_address)
        #
        # self.assertTrue(balance2_after is not 0, 'cash was not send to address: ' + self.second_address)