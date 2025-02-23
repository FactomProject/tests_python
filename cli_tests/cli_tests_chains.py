import unittest, os, binascii, time, hashlib

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address

@attr(fast=True)
class CLITestsChains(unittest.TestCase):
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    api_factomd = APIObjectsFactomd()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('shared_test_data.json')

    TIME_TO_WAIT = 5

    def setUp(self):
        self.ecrate = self.cli_create.get_entry_credit_rate()
        imported_addresses = self.cli_create.import_addresses(self.data['factoid_wallet_address'],
                                                              self.data['ec_wallet_address'])
        self.first_address = imported_addresses[0]
        self.entry_credit_address = imported_addresses[1]

    def test_make_chain_with_wrong_address(self):
        data = create_random_string(1024)
        names_list = ['-n', '1', '-n', '1']
        self.assertTrue("is not an Entry Credit Public Address" in self.cli_chain.make_chain('bogus', data, external_id_list=names_list))

    def test_make_chain_with_factoids_not_ec(self):
        data = create_random_string(1024)
        names_list = ['-n', '1', '-n', '1']
        self.assertTrue("is not an Entry Credit Public Address" in self.cli_chain.make_chain(self.first_address, data, external_id_list=names_list))

    def test_make_correct_chain_with_not_enough_ec(self):
        self.entry_credit_address0 = fund_entry_credit_address(0)
        data = create_random_string(1024)
        names_list = ['-n', create_random_string(5), '-n', create_random_string(5)]
        self.assertTrue(
            'Not enough Entry Credits' in self.cli_chain.make_chain(self.entry_credit_address0, data, external_id_list=names_list))

    def test_make_chain_that_already_exists(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.cli_chain.make_chain(self.entry_credit_address100, data,
                                  external_id_list=names_list)

        # look for chainhead by external id
        wait_for_chain_in_block(external_id_list=names_list)
        self.assertTrue('PrevKeyMR: 0000000000000000000000000000000000000000000000000000000000000000' in self.cli_chain.get_chainhead(external_id_list=names_list), 'Chainhead not found')

        # try to make duplicate chain
        self.assertTrue('already exists' in self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list), "Duplicate chain not detected")

        # try to compose duplicate chain
        self.assertTrue('already exist' in self.cli_chain.compose_chain(self.entry_credit_address100, data, external_id_list=names_list), "Duplicate chain not detected")

    def test_make_chain_and_check_balance(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-E']
        balance_before = self.cli_create.check_wallet_address_balance(self.entry_credit_address100)
        entry_hash = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
        self.assertTrue("Entry not found" not in self.cli_chain.get_entry_by_hash(entry_hash),
                        "Chain not revealed")
        balance_after = self.cli_create.check_wallet_address_balance(self.entry_credit_address100)
        self.assertEqual(int(balance_before), int(balance_after) + 12, 'Incorrect charge for chain creation')

    def test_make_chain_and_check_chainhead(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-f', '-C']
        chainid = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
        found = False
        for x in range(0, self.TIME_TO_WAIT):
            if 'Chain not yet included in a Directory Block' in self.cli_chain.get_allentries(chain_id=chainid):
                found = True
                break
            time.sleep(1)
        self.assertTrue(found, 'Chainhead is missing')
        for x in range(0, self.blocktime):
            if 'Chain not yet included in a Directory Block' not in self.cli_chain.get_allentries(chain_id=chainid):
                found = True
                break
            time.sleep(1)
        self.assertTrue(found, 'Chainhead not included in a Directory Block after 1 block')

    # # TODO reinstate this test when FD-547 is implemented to make it work
    # def test_raw_commit(self):
    #     # Currently this test fails about every 3-7 times. FD-547 to fix it is in backlog.
    #
    #     self.entry_credit_address100 = fund_entry_credit_address(100)
    #     print 'balance', self.cli_create.check_wallet_address_balance(self.entry_credit_address100)
    #     for _ in range(10):
    #         data = create_random_string(1024)
    #         name_1 = create_random_string(5)
    #         name_2 = create_random_string(5)
    #         names_list = ['-n', name_1, '-n', name_2]
    #         # chain_flag_list = ['-T']
    #         text = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list)
    #         print 'text', text
    #         chain_dict = self.cli_chain.parse_simple_data(text)
    #         chain_id = chain_dict['ChainID']
    #         tx_id = chain_dict['CommitTxID']
    #         # tx_id = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
    #         wait_for_ack(tx_id)
    #         print 'wait before raw tx_id', tx_id
    #         raw = self.cli_create.get_raw(tx_id)
    #         wait_for_ack(tx_id)
    #         print 'wait after raw tx_id', tx_id
    #         print 'raw', raw
    #
    #         # exclude public key and signature (last 32 + 64 bytes = 192 characters)
    #         raw_trimmed = raw[:-192]
    #
    #         # convert to binary
    #         serialized_raw = binascii.unhexlify(raw_trimmed)
    #
    #         # hash via SHA256
    #         hashed256_raw = hashlib.sha256(serialized_raw).hexdigest()
    #         print 'hashed256_raw', hashed256_raw
    #
    #         self.assertEqual(hashed256_raw, tx_id, 'Raw data string is not correct')
    #
    # # TODO remove this helper code when FD-547 is implemented
    # def test_many_raw(self):
    #     # This test is just to run the previous test many times because it fails only about every 3-7 times.
    #     for run in range(0,100):
    #         print
    #         print 'run', run+1
    #         self.test_raw_commit()
    #         # print 'i', i

    # TODO remove this helper code when FD-547 is implemented
    # def test_one_raw(self):
    #     raw = self.cli_create.get_raw('821299679ceebb84c21ca609acd7ddf5a6f3b4ff17e51324ae049722293cc10c')
    #     print 'raw', raw

    def test_make_chain_with_hex_external_id_return_chain_id(self):
        ''' This test is only reliable for the 1st run on a given database.
         Because of the -C flag, no transaction id is available, so the only way to locate the created chain is by
         using a fixed external id which yields a known entry hash. However once this chain is created in a database,
         it will still be there even if subsequent runs fail.
         '''
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = 'a'*1024
        name_1 = binascii.b2a_hex(str.encode(self.data['1st_hex_external_id1'])).decode('UTF-8')
        name_2 = binascii.b2a_hex(str.encode(self.data['1st_hex_external_id2'])).decode('UTF-8')
        names_list = ['-h', name_1, '-h', name_2]
        chain_flag_list = ['-E']
        self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
        self.assertTrue('Entry not found' not in self.cli_chain.get_entry_by_hash(self.data[
                                                                                      '1st_hex_entry_hash']), 'Entry not found')

        # validate get firstentry by hex external id command
        wait_for_chain_in_block(external_id_list=names_list)
        text = self.cli_chain.get_firstentry(external_id_list=names_list)
        chain_id = self.cli_chain.parse_entry_data(text)['ChainID']
        self.assertTrue(chain_id == self.data['1st_hex_chain_id'], 'Chain not found')

    def test_force_make_chain(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        factom_flags_list = ['-f', '-T']
        tx_id = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=factom_flags_list)
        wait_for_ack(tx_id)
        self.assertTrue("TransactionACK" in self.cli_create.request_transaction_acknowledgement(tx_id), 'Forced chain not acknowledged')

    def test_quiet_make_chain(self):
        ''' This test is only reliable on the 1st run on a given database.
         Because of the -q flag, no transaction id is available, so the only way to locate the created chain is by
         using a fixed external id which yields a known entry hash. However once this chain is created in a database,
         it will still be there even if subsequent runs fail.
         '''
        data = 'z'*1024
        self.entry_credit_address100 = fund_entry_credit_address(100)
        name_1 = self.data['1st_external_id1']
        name_2 = self.data['1st_external_id2']
        names_list = ['-n', name_1, '-n', name_2]
        factom_flags_list = ['-q']
        self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=factom_flags_list)
        self.assertNotIn('Entry not found', self.cli_chain.get_entry_by_hash(self.data['1st_entry_hash']))

    def test_compose_chain(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        text = self.cli_chain.compose_chain(self.entry_credit_address100, data, external_id_list=names_list)
        start = text.find('"message":"') + 11
        end = text.find('"},"method', start)
        self.api_factomd.commit_chain(text[start:end])
        self.assertTrue("commit-chain" and "reveal-chain" in text)

    def test_compose_chain_with_hex_external_id(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = binascii.b2a_hex(os.urandom(2)).decode('UTF-8')
        name_2 = binascii.b2a_hex(os.urandom(2)).decode('UTF-8')
        names_list = ['-h', name_1, '-h', name_2]
        text = self.cli_chain.compose_chain(self.entry_credit_address100, data, external_id_list=names_list)
        start = text.find('"message":"') + 11
        end = text.find('"},"method', start)
        self.api_factomd.commit_chain(text[start:end])
        self.assertTrue("commit-chain" and "reveal-chain" in text)

    def test_compose_chain_with_zero_ec(self):
        self.entry_credit_address0 = fund_entry_credit_address(0)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.assertTrue("Not enough Entry Credits" in self.cli_chain.compose_chain(self.entry_credit_address0, data, external_id_list=names_list), "Zero Entry Credit balance not detected")

        # force compose chain
        factom_flags_list = ['-f']
        self.assertTrue("curl" in self.cli_chain.compose_chain(self.entry_credit_address0, data, external_id_list=names_list, flag_list=factom_flags_list), "Zero Entry Credit balance compose chain not forced")

    def test_compose_chain_with_not_enough_ec(self):
        self.entry_credit_address10 = fund_entry_credit_address(10)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.assertTrue("Not enough Entry Credits" in self.cli_chain.compose_chain(self.entry_credit_address10, data, external_id_list=names_list), "Insufficient balance not detected")

    def test_check_chain_height(self):
        # get latest block sequence number
        text = self.cli_chain.get_latest_directory_block()
        seq = self.cli_chain.parse_block_data(text)['SequenceNumber']

        # compare to block sequence number given by get heights
        self.assertTrue(seq == self.cli_chain.get_directory_block_height_from_head(), 'Directory block is not equal to sequence number')

        # get latest block previous merkel root
        prevMR = self.cli_chain.parse_block_data(text)['PrevKeyMR']

        # compare to previous merkel root given by looking up directory block merkel root
        keyMR = self.cli_chain.parse_block_data(text)['KeyMR']

        text = self.cli_chain.get_directory_block(keyMR)
        self.assertTrue(prevMR == self.cli_chain.parse_block_data(text)['PrevKeyMR'], 'Get dblock by merkle root did not fetch correct directory block')

    def test_get_directory_block_by_merkel_root(self):
        factom_flags_list = ['-K']
        keyMR = self.cli_chain.get_latest_directory_block(flag_list=factom_flags_list)
        self.assertFalse('Block not found' in self.cli_chain.get_directory_block(keyMR), 'Bad merkel root')


