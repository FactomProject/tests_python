import unittest, time

from nose.plugins.attrib import attr
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address

'''
This bulk test checks for the rare occurrence of a chain being created and the server returning a server error
rather than a Chain ID.
Many chains are created because the error is rare.
'''

NUMBER_OF_ENTRIES = 1000

@attr(load=True)
class CLITestsMakeDuplicateEntries(unittest.TestCase):
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()

    def setUp(self):
        # self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_make_entry_return_entry_hash(self):
        # make chain
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.cli_chain.make_chain(self.entry_credit_address1000, data, external_id_list=names_list)

        # make entry
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-E', '-f']
        for x in range(NUMBER_OF_ENTRIES):
            entry_hash = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000, data, external_id_list=names_list, flag_list=factom_flags_list)
            print('entry_hash', entry_hash)
            print('sleeping for 60 seconds...')
            print()
            time.sleep(60)
            self.assertNotIn("Entry not found", self.cli_chain.get_entry_by_hash(entry_hash), "Entry not revealed")

