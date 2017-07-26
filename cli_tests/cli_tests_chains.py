import unittest
import os, binascii

from nose.plugins.attrib import attr
from flaky import flaky

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from api_objects.api_objects_factomd import APIObjectsFactomd

from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_entry_in_block, fund_entry_credit_address

@flaky(max_runs=3, min_passes=1)
@attr(fast=True)
class CLITestsChains(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    TIME_TO_WAIT = 5

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.chain_objects = CLIObjectsChain()
        self.api_objects = APIObjectsFactomd()
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.first_address = self.cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.entry_credit_address = self.cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])

    def test_make_chain_with_wrong_address(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        names_list = ['-n', '1', '-n', '1']
        self.assertTrue("is not an Entry Credit Public Address" in self.chain_objects.make_chain_from_binary_file('bogus', path, external_id_list=names_list))

    def test_make_chain_with_factoids_not_ec(self):
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        names_list = ['-n', '1', '-n', '1']
        self.assertTrue("is not an Entry Credit Public Address" in self.chain_objects.make_chain_from_binary_file(self.first_address, path, external_id_list=names_list))

    def test_make_correct_chain_with_not_enough_ec(self):
        self.entry_credit_address0 = fund_entry_credit_address(0)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        names_list = ['-n', create_random_string(5), '-n', create_random_string(5)]
        self.assertTrue(
            'Not enough Entry Credits' in self.chain_objects.make_chain_from_binary_file(self.entry_credit_address0, path, external_id_list=names_list))

    def test_make_chain_that_already_exists(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.chain_objects.make_chain_from_binary_file(self.entry_credit_address100, path,
                                                       external_id_list=names_list)

        # look for chainhead by external id
        wait_for_entry_in_block(external_id_list=names_list)
        self.assertTrue('PrevKeyMR: 0000000000000000000000000000000000000000000000000000000000000000' in self.chain_objects.get_chainhead(external_id_list=names_list), 'Chainhead not found')

        # try to make duplicate chain
        self.assertTrue('already exists' in self.chain_objects.make_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list), "Duplicate chain not detected")

        # try to compose duplicate chain
        self.assertTrue('already exist' in self.chain_objects.compose_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list), "Duplicate chain not detected")

    def test_make_chain_and_check_balance(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-E']
        balance_before = self.cli_create.check_wallet_address_balance(self.entry_credit_address100)
        entry_hash = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list, flag_list=chain_flag_list)
        self.assertTrue("Entry not found" not in self.chain_objects.get_entry_by_hash(entry_hash),
                        "Chain not revealed")
        balance_after = self.cli_create.check_wallet_address_balance(self.entry_credit_address100)
        self.assertEqual(balance_before, balance_after + 12, 'Incorrect charge for chain creation')

    def test_make_chain_with_hex_external_id_return_chain_id(self):
        ''' This test is only reliable for the 1st run on a given database.
         Because of the -C flag, no transaction id is available, so the only way to locate the created chain is by
         using a fixed external id which yields a known entry hash. However once this chain is created in a database,
         it will still be there even if subsequent runs fail.'''

        self.entry_credit_address100 = fund_entry_credit_address(100)
        # path = '/home/factom/PyCharm/tests_python/test_data/testfile'
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['1st_hex_external_id1']
        name_2 = self.data['1st_hex_external_id2']
        names_list = ['-h', name_1, '-h', name_2]
        chain_flag_list = ['-C']
        self.chain_objects.make_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list, flag_list=chain_flag_list)
        self.assertTrue("Entry not found" not in self.chain_objects.get_entry_by_hash(self.data[
                          '1st_hex_entry_hash']))

        # validate get firstentry by hex external id command
        wait_for_entry_in_block(external_id_list=names_list)
        text = self.chain_objects.get_firstentry(external_id_list=names_list)
        chain_id = self.chain_objects.parse_entry_data(text)['ChainID']
        self.assertTrue(chain_id == self.data['1st_hex_chain_id'], 'Chain not found')

    def test_force_make_chain(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        factom_flags_list = ['-f', '-T']
        tx_id = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list, flag_list=factom_flags_list)
        wait_for_ack(tx_id)
        self.assertTrue("TransactionACK" in self.cli_create.request_transaction_acknowledgement(tx_id), 'Forced chain not acknowledged')

    def test_quiet_make_chain(self):
        ''' This test is only reliable on the 1st run on a given database.
         Because of the -q flag, no transaction id is available, so the only way to locate the created chain is by
         using a fixed external id which yields a known entry hash. However once this chain is created in a database,
         it will still be there even if subsequent runs fail.'''

        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        self.entry_credit_address100 = fund_entry_credit_address(100)
        name_1 = self.data['1st_external_id1']
        name_2 = self.data['1st_external_id2']
        names_list = ['-n', name_1, '-n', name_2]
        factom_flags_list = ['-q']
        self.chain_objects.make_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list, flag_list=factom_flags_list)
        self.assertTrue("Entry not found" not in self.chain_objects.get_entry_by_hash(self.data[
                                                    '1st_entry_hash']))

    def test_compose_chain(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        text = self.chain_objects.compose_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list)
        start = text.find('"message":"') + 11
        end = text.find('"},"method', start)
        self.api_objects.commit_chain_by_message(text[start:end])
        self.assertTrue("commit-chain" and "reveal-chain" in text)

    def test_compose_chain_with_hex_external_id(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        names_list = ['-h', name_1, '-h', name_2]
        text = self.chain_objects.compose_chain_from_binary_file(self.entry_credit_address100, path, external_id_list=names_list)
        start = text.find('"message":"') + 11
        end = text.find('"},"method', start)
        self.api_objects.commit_chain_by_message(text[start:end])
        self.assertTrue("commit-chain" and "reveal-chain" in text)

    def test_compose_chain_with_zero_ec(self):
        self.entry_credit_address0 = fund_entry_credit_address(0)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.assertTrue("Not enough Entry Credits" in self.chain_objects.compose_chain_from_binary_file(self.entry_credit_address0, path, external_id_list=names_list), "Zero Entry Credit balance not detected")

        # force compose chain
        factom_flags_list = ['-f']
        self.assertTrue("curl" in self.chain_objects.compose_chain_from_binary_file(self.entry_credit_address0, path, external_id_list=names_list, flag_list=factom_flags_list), "Zero Entry Credit balance compose chain not forced")

    def test_compose_chain_with_not_enough_ec(self):
        self.entry_credit_address10 = fund_entry_credit_address(10)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.assertTrue("Not enough Entry Credits" in self.chain_objects.compose_chain_from_binary_file(self.entry_credit_address10, path, external_id_list=names_list), "Insufficient balance not detected")

    def test_check_chain_height(self):

        # get latest block sequence number
        text = self.chain_objects.get_latest_directory_block()
        seq = self.chain_objects.parse_block_data(text)['SequenceNumber']

        # compare to block sequence number given by get heights
        self.assertTrue(seq == self.chain_objects.get_directory_block_height_from_head(), 'Directory block is not equal to sequence number')

        # get latest block previous merkel root
        prevMR = self.chain_objects.parse_block_data(text)['PrevBlockKeyMR']

        # compare to previous merkel root given by looking up directory block merkel root
        keyMR = self.chain_objects.parse_block_data(text)['DBlock']
        text = self.chain_objects.get_directory_block(keyMR)
        self.assertTrue(prevMR == self.chain_objects.parse_block_data(text)[
    'PrevBlockKeyMR'], 'Get dblock by merkle root did not fetch correct directory block')

    def test_get_directory_block_by_merkel_root(self):
        factom_flags_list = ['-K']
        keyMR = self.chain_objects.get_latest_directory_block(flag_list=factom_flags_list)
        self.assertFalse('Block not found' in self.chain_objects.get_directory_block(keyMR), 'Bad merkel root')
