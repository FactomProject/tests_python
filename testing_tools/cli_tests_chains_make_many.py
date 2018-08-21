import unittest

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from api_objects.api_objects_factomd import APIObjectsFactomd

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address

'''This bulk test checks for the rare occurrence of a chain being created and the server returning a server error
rather than a Chain ID.
Many chains are created because the error is rare.
'''

NUMBER_OF_RUNS = 200000

@attr(load=True)
class CLITestsChainsMakeMany(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.chain_objects = CLIObjectsChain()
        self.api_objects = APIObjectsFactomd()

    def test_make_chain_and_check_balance(self):
        self.entry_credit_address = fund_entry_credit_address(NUMBER_OF_RUNS * 12)
        content = create_random_string(1024)
        for i in range(NUMBER_OF_RUNS):
            # this print statement is necessary to monitor the test progress
            print 'Chain', i + 1
            name_1 = create_random_string(5)
            name_2 = create_random_string(5)
            names_list = ['-n', name_1, '-n', name_2]
            self.assertFalse("looking for beginning of value" in self.chain_objects.make_chain(self.entry_credit_address, content, external_id_list=names_list), "Chain creation failed on chain " + str(i) + " with external ids " + str(names_list))
