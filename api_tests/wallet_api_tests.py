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

        self.ecrate = self.factomd_api_objects.get_entry_credits_rate()
        self.ecrate
        self.entry_creds_wallet2 = self.wallet_api_objects.import_addres_by_secret('Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        self.entry_creds_wallet2 = self.wallet_api_objects.generate_ec_address()

    def alocate_founds_to_factoid_walled_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_factoid_input_to_transaction(transaction_name, self.first_address, '1')
        self.wallet_api_objects.add_factoid_output_to_transaction(transaction_name, self.second_address, '1')
        self.wallet_api_objects.substract_fee_in_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        self.wallet_api_objects.compose_transaction(transaction_name)



