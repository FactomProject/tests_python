import unittest
import os

from api_objects.factom_cli_create import FactomCliCreate
from api_objects.factom_chain_objects import FactomChainObjects

class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(
            "Fs2DNirmGDtnAZGXqca3XHkukTNMxoMGFFQxJA3bAjJnKzzsZBMH")
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"salute umbrella proud setup delay ginger practice split toss jewel tuition stool"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            'Es2Rf7iM6PdsqfYCo3D1tnAR65SkLENyWJG1deUzpRMQmbh9F3eG')
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def test_make_chain_with_wrong_address(self):
        path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
        self.assertTrue("not an Entry" in self.factom_chain_object.make_chain('bogus', path, '1', '1'))
