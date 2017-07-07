import unittest
import os
import time

from nose.plugins.attrib import attr

from cli_objects.factom_cli_objects import FactomCliMainObjects
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address
from random import randint

@attr(load_tool=True)
class FactomLoadNodes(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliMainObjects()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(
            self.data['factoid_wallet_address'])
        self.ecrate = self.factom_cli_create.get_entry_credit_rate()
        self.entry_credit_address1000000 = fund_entry_credit_address(1000000)

    def test_make_chain_and_check_balance(self):

        # BLOCKTIME and ENTRIES_PER_BLOCK are variables in shared_test_dat.json
        # increasing ENTRIES_PER_BLOCK decreases sleep time between entries
        # set CONTINUOUS for no sleeping at all

        CONTINUOUS = True

        print 'sleep time', float(self.data['BLOCKTIME']) / float(self.data['ENTRIES_PER_BLOCK'])
        self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address1000000)
        chain_flags_list = ['-f', '-C']
        for i in xrange(20):
            path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')

            for i in range(80):
                with open('output_file', 'wb') as fout:
                    fout.write(os.urandom(randint(100, 5000)))
                    path = fout.name
                name_1 = create_random_string(5)
                name_2 = create_random_string(5)
                names_list = ['-n', name_1, '-n', name_2]
                chain_id = self.factom_chain_object.make_chain_from_binary_file(self.entry_credit_address1000000, path, external_id_list=names_list, flag_list=chain_flags_list)

                for i in range(120):
                    with open('output_file', 'wb') as fout:
                        fout.write(os.urandom(randint(100, 5000)))
                        path = fout.name
                    name_1 = create_random_string(5)
                    name_2 = create_random_string(5)
                    names_list = ['-c', chain_id, '-e', name_1, '-e', name_2]
                    self.factom_chain_object.add_entry_to_chain(self.entry_credit_address1000000, path, external_id_list=names_list, flag_list=chain_flags_list)
                    if not CONTINUOUS: time.sleep(float(self.data['BLOCKTIME']) / float(self.data['ENTRIES_PER_BLOCK']) * 0.2)
                    self.assertFalse('0' == self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address1000000), 'out of entry credits')
            os.remove(path)
