import unittest, time
import os

from nose.plugins.attrib import attr
from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address
from random import randint

@attr(load_tool=True)
class CLITestsLoadNodes(unittest.TestCase):

    data = read_data_from_json('shared_test_data.json')
    blocktime = os.environ['BLOCKTIME']

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.chain_objects = CLIObjectsChain()
        self.first_address = self.cli_create.import_addresses(self.data['factoid_wallet_address'])[0]
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_credit_address1000000 = fund_entry_credit_address(1000000)

    def test_make_chain_and_check_balance(self):
        '''
        ENTRIES in block is defined in shared_test_data.json,
        blocktime is value passed to docker container at start
        increasing ENTRIES_PER_BLOCK decreases sleep time between entries.
        set CONTINUOUS for no sleeping at all.
        '''
        CONTINUOUS = True
        # print statement is necessary to see the calculated sleep time
        print 'sleep time', float(self.blocktime) / float(self.data['ENTRIES_PER_BLOCK'])
        self.cli_create.check_wallet_address_balance(self.entry_credit_address1000000)
        chain_flags_list = ['-f', '-C']
        for i in xrange(20):
            for i in range(80):
                name_1 = create_random_string(5)
                name_2 = create_random_string(5)
                names_list = ['-n', name_1, '-n', name_2]
                content = create_random_string(randint(100, 5000))
                chain_id = self.chain_objects.make_chain(self.entry_credit_address1000000, content, external_id_list=names_list, flag_list=chain_flags_list)

                for i in range(120):
                    name_1 = create_random_string(5)
                    name_2 = create_random_string(5)
                    names_list = ['-c', chain_id, '-e', name_1, '-e', name_2]
                    content = create_random_string(randint(100, 5000))
                    self.chain_objects.add_entry_to_chain(self.entry_credit_address1000000, content, external_id_list=names_list, flag_list=chain_flags_list)
                    if not CONTINUOUS: time.sleep(float(self.blocktime) / float(self.data['ENTRIES_PER_BLOCK']) * 0.2)
                    self.assertFalse('0' == self.cli_create.check_wallet_address_balance(self.entry_credit_address1000000), 'out of entry credits')

