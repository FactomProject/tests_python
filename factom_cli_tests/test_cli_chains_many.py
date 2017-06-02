import unittest
import os, binascii
import time

from nose.plugins.attrib import attr
from flaky import flaky

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from api_objects.factomd_api_objects import FactomApiObjects

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, fund_entry_credit_address

'''This bulk test checks for the rare occurrence of a chain being created and the server returning a server error
rather than a Chain ID.
Many chains are created because the error is rare.
@attr(fast=False) because it takes a long time and shouldn't be run regularly'''

NUMBER_OF_RUNS = 200000

@attr(fast=False)
class FactomChainTests(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.factomd_api_objects = FactomApiObjects()

    def test_make_chain_and_check_balance(self):
        self.entry_credit_address = fund_entry_credit_address(NUMBER_OF_RUNS * 12)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        for i in range(NUMBER_OF_RUNS):
            print 'Chain', i + 1
            name_1 = create_random_string(5)
            name_2 = create_random_string(5)
            names_list = ['-n', name_1, '-n', name_2]
            self.assertFalse("looking for beginning of value" in self.factom_chain_object.make_chain_from_binary_file(self.entry_credit_address, path, names_list), "Chain creation failed on chain " + str(i) + " with external ids " + str(names_list))
