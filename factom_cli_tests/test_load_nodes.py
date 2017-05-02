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
        chain_flags_list = ['-f ', '-C ']
        for i in xrange(10):
            path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
            self.factom_cli_create.force_buy_ec(self.first_address, self.entry_creds_wallet1, '100')



            for i in range(80):
                with open('output_file', 'wb') as fout:
                    fout.write(os.urandom(randint(100, 5000)))
                    path = fout.name
                name_1 = create_random_string(5)
                name_2 = create_random_string(5)
                names_list = ['-n', name_1, '-n', name_2]
                chain_id = self.factom_chain_object.make_chain_from_binary(self.entry_creds_wallet1, path, names_list,
                                                                           flag_list=chain_flags_list)

                for i in range(120):
                    with open('output_file', 'wb') as fout:
                        fout.write(os.urandom(randint(100, 5000)))
                        path = fout.name
                    name_1 = create_random_string(5)
                    name_2 = create_random_string(5)
                    names_list = ['-e', name_1, '-e', name_2]
                    self.factom_chain_object.add_entries_to_chain(self.entry_creds_wallet1, path, chain_id, names_list)
                    time.sleep(2)
                    os.remove(path)
            time.sleep(5)
        time.sleep(30)
