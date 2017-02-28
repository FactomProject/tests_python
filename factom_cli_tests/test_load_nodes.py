import unittest
import os
import time

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string, read_data_from_json
from random import randint

@attr(load=True)
class FactomLoadNodes(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(
            self.data['factoid_wallet_address'])
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()


    def test_make_chain_and_check_balance(self):
        for i in xrange(10):
            path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
            self.factom_cli_create.buy_ec(self.first_address, self.entry_creds_wallet1, '100')


            name_1 = create_random_string(5)
            name_2 = create_random_string(5)
            for i in range(80):
                with open('output_file', 'wb') as fout:
                    fout.write(os.urandom(randint(100, 5000)))
                    path = fout.name
                chain_id = self.factom_chain_object.force_make_chain_from_binary_file_and_receive_chain_id(self.entry_creds_wallet1, path, name_1, name_2)

                for i in range(120):
                    with open('output_file', 'wb') as fout:
                        fout.write(os.urandom(randint(100, 5000)))
                        path = fout.name
                    name_1 = create_random_string(5)
                    name_2 = create_random_string(5)
                    self.factom_chain_object.add_entries_to_chain(self.entry_creds_wallet1, path, chain_id, name_1, name_2)
                    os.remove(path)
            time.sleep(5)
        time.sleep(30)



