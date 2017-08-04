import unittest
import os, binascii, hashlib

from flaky import flaky

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_entry_in_block, fund_entry_credit_address
from nose.plugins.attrib import attr

@flaky(max_runs=3, min_passes=1)
@attr(fast=True)
class CLITestsEntries(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    path = ''

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.chain_objects = CLIObjectsChain()
        self.first_address = self.cli_create.import_address(self.data['factoid_wallet_address'])
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def tearDown(self):
        if self.path:
            os.remove(self.path)

    def test_make_entry_return_entry_hash(self):
        # make chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, path, external_id_list=names_list)

        # make entry
        with open('output_file', 'a') as fout:
            fout.write(os.urandom(1))
            self.path = fout.name
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-E']
        entry_hash = self.chain_objects.add_entry_to_chain(self.entry_credit_address1000, self.path, external_id_list=names_list, flag_list=factom_flags_list)
        self.assertNotIn("Entry not found", self.chain_objects.get_entry_by_hash(entry_hash),
                        "Entry not revealed")

    def test_raw_entry(self):
        # make chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        factom_flags_list = ['-E']
        entry_hash = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, path, external_id_list=names_list, flag_list=factom_flags_list)
        raw = self.chain_objects.get_raw(entry_hash)

        # convert to binary
        serialized_raw = binascii.unhexlify(raw)

        # hash via SHA512
        hashed512_raw = hashlib.sha512(serialized_raw).digest()

        # concatenate SHA512 hash binary result and serialized raw data
        prepended_raw = hashed512_raw + serialized_raw

        # hash via SHA256 the concatenated data
        hashed256_raw = hashlib.sha256(prepended_raw).hexdigest()

        self.assertEqual(hashed256_raw, entry_hash, 'Raw data string is not correct')

    def test_verify_entry_costs(self):
        # create chain
        ONE_K_MINUS_8 = 1016
        '''entry cost = 1 ec per 1024 bytes
        overhead = total length of external ids + 2 bytes per external id
        There are 2 external ids of 2 bytes each
        1024 - 4(2 external ids x 2 bytes length) - 4(2 bytes x 2 external ids) = 1016'''

        MAX_ENTRY_SIZE_MINUS_7 = 10233
        '''largest allowable entry is 10K = 10240 bytes
        smallest too large entry = 10241 bytes
        10241 - 4(2 external ids x 2 bytes length) - 4(2 bytes x 2 external id) = 10233'''

        chain_name_1 = create_random_string(5)
        chain_name_2 = create_random_string(5)
        chain_names_list = ['-n', chain_name_1, '-n', chain_name_2]
        firstentry_ext_id = chain_name_1

        i = ONE_K_MINUS_8
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(i))
            self.path = fout.name
        text = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, self.path, external_id_list=chain_names_list)
        chain_dict = self.chain_objects.parse_simple_data(text)
        chain_id = chain_dict['ChainID']
        tx_id = chain_dict['CommitTxID']
        wait_for_ack(tx_id)
        balance_1st = self.cli_create.check_wallet_address_balance(self.entry_credit_address1000)

        # write entries
        while i < MAX_ENTRY_SIZE_MINUS_7:
            # write largest entry for fee amount
            name_1 = create_random_string(2)
            name_2 = create_random_string(2)
            names_list = chain_names_list + ['-e', name_1, '-e', name_2]
            text = self.chain_objects.add_entry_to_chain(self.entry_credit_address1000,
                                                         self.path, external_id_list=names_list)
            tx_id = self.chain_objects.parse_simple_data(text)['CommitTxID']
            wait_for_ack(tx_id)
            balance_last = self.cli_create.check_wallet_address_balance(self.entry_credit_address1000)
            self.assertEqual(int(balance_1st), int(balance_last) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            # write smallest entry for fee amount
            i += 1
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1))
            if i == MAX_ENTRY_SIZE_MINUS_7:
                break
            name_1 = binascii.b2a_hex(os.urandom(2))
            name_2 = binascii.b2a_hex(os.urandom(2))
            names_list = ['-c', chain_id, '-x', name_1, '-x', name_2]
            text = self.chain_objects.add_entry_to_chain(self.entry_credit_address1000,
                                                         self.path, external_id_list=names_list)
            tx_id = self.chain_objects.parse_simple_data(text)['CommitTxID']
            wait_for_ack(tx_id)
            balance_1st = self.cli_create.check_wallet_address_balance(self.entry_credit_address1000)
            self.assertEqual(int(balance_last), int(balance_1st) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            i += 1023
            with open('output_file', 'a') as fout:
                fout.write(os.urandom(1023))

        # write too large entry
        name_1 = create_random_string(2)
        name_2 = create_random_string(2)
        names_list = ['-c', chain_id, '-e', name_1, '-e', name_2]

        self.assertIn("Entry cannot be larger than 10KB", self.chain_objects.add_entry_to_chain(self.entry_credit_address1000, self.path, external_id_list=names_list))

        # check for pending entries
        self.assertIn(chain_id, self.chain_objects.get_pending_entries(), 'Entry not shown as pending')

        # validate get firstentry command
        wait_for_entry_in_block(external_id_list=chain_names_list)
        self.assertIn("ExtID: " + firstentry_ext_id, self.chain_objects.get_firstentry(external_id_list=chain_names_list), 'Chain not found')

        # validate get firstentry_return_entry_hash
        factom_flags_list = ['-E']
        entry_hash = self.chain_objects.get_firstentry(flag_list=factom_flags_list, chain_id=chain_id)
        self.assertTrue(entry_hash and "Entry [0]" in self.chain_objects.get_allentries(chain_id=chain_id),
                        'Entry not found')

    def test_force_make_entry_with_hex_external_chain_id(self):
        # make chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        chain_names_list = ['-h', name_1, '-h', name_2]
        text = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, path, external_id_list=chain_names_list)
        chain_id = self.chain_objects.parse_simple_data(text)['ChainID']
        entry_hash = self.chain_objects.parse_simple_data(text)['Entryhash']

        # make entry
        with open('output_file', 'a') as fout:
            fout.write(os.urandom(1))
            self.path = fout.name
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-f', '-T']
        tx_id = self.chain_objects.add_entry_to_chain(self.entry_credit_address1000,
                                                      self.path, external_id_list=names_list, flag_list=factom_flags_list)

        # check for pending entries return entry hash
        factom_flags_list = ['-E']
        entry_hash_list = self.chain_objects.get_pending_entries(flag_list=factom_flags_list)
        for entry_hash in entry_hash_list.split('\n'):
            text = self.chain_objects.get_entry_by_hash(entry_hash)

            entry_chain_id = self.chain_objects.parse_entry_data(text)['ChainID']
            if entry_chain_id == chain_id:
               found = True
               break
        self.assertTrue(found, 'Entry not shown as pending')

        wait_for_ack(tx_id)
        self.assertIn("TransactionACK", self.cli_create.request_transaction_acknowledgement(tx_id),
                        "Forced entry was not revealed")

        # compose entry by external chain id
        self.assertTrue(
            "message" and "entry" in self.chain_objects.compose_entry_from_binary_file(self.entry_credit_address1000, self.path, external_id_list=names_list))
        # wait for entry to arrive in block
        wait_for_entry_in_block(external_id_list=chain_names_list)

        # look for chainhead by hex external id
        text = self.chain_objects.get_chainhead(external_id_list=chain_names_list)
        self.assertIn('PrevKeyMR: 0000000000000000000000000000000000000000000000000000000000000000', text, 'Chainhead not found')

        # look for chainhead by hex external id return KeyMR
        keyMR = self.chain_objects.parse_block_data(text)['EBlock']
        # keyMR = self.factom_chain_object.parse_entryblock_data(text)['fixed']['EBlock']
        factom_flags_list = ['-K']
        self.assertEqual(keyMR, self.chain_objects.get_chainhead(external_id_list=chain_names_list, flag_list=factom_flags_list), 'Key merkle root does not match')

        # check get allentries by hex external id
        factom_flags_list = [' -E']
        self.assertIn(entry_hash, self.chain_objects.get_allentries(flag_list=factom_flags_list, external_id_list=chain_names_list), 'Chain not found')

    def test_quiet_make_entry(self):
        ''' This test is only reliable on the 1st run on a given database.
          Because of the -q flag, no transaction id is available, so the only way to locate the created entry is by
          using a fixed entry in a fixed chain id which yields a known entry hash. However once this entry is created
          in a database, it will still be there even if subsequent runs fail.'''

        # make chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = self.data['2nd_external_id1']
        name_2 = self.data['2nd_external_id2']
        names_list = ['-n', name_1, '-n', name_2]
        self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, path, external_id_list=names_list)

        # make entry
        with open('output_file', 'a') as fout:
            fout.write('1')
            self.path = fout.name
        name_1 = self.data['3rd_over_2nd_external_id1']
        name_2 = self.data['3rd_over_2nd_external_id2']
        entry_names_list = names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-q']
        self.chain_objects.add_entry_to_chain(self.entry_credit_address1000, self.path, external_id_list=entry_names_list, flag_list=factom_flags_list)
        self.assertNotIn("Entry not found", self.chain_objects.get_entry_by_hash(self.data['3rd_over_2nd_entry_hash']))

        # check get allentries by external id and returning entry hash
        factom_flags_list = ['-E']
        self.assertIn(self.data['3rd_over_2nd_entry_hash'], self.chain_objects.get_allentries(external_id_list=names_list, flag_list=factom_flags_list), "Entry not found")

    def test_make_entry_return_chain_id(self):

        # make chain
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        chain_name_1 = create_random_string(5)
        chain_name_2 = create_random_string(5)
        chain_names_list = ['-n', chain_name_1, '-n', chain_name_2]
        factom_flags_list = ['-C']
        chain_id = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, path, external_id_list=chain_names_list, flag_list=factom_flags_list)

        # make entry
        with open('output_file', 'a') as fout:
            fout.write('1')
            self.path = fout.name
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        entry_chain_id = self.chain_objects.add_entry_to_chain(self.entry_credit_address1000, self.path, external_id_list=names_list, flag_list=factom_flags_list)

        # wait for entry to arrive in block
        wait_for_entry_in_block(external_id_list=chain_names_list)

        self.assertEqual(entry_chain_id, chain_id, 'Chain Id of Entry does not match Chain ID of chain')
        self.assertIn(entry_chain_id, self.chain_objects.get_allentries(chain_id=chain_id), "Entry not found")

        # look for chainhead by chain id
        self.assertIn('ChainID: ' + entry_chain_id, self.chain_objects.get_chainhead(chain_id=chain_id), 'Chainhead not found')

    def test_compose_entry(self):
        # make chain
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        chain_names_list = ['-n', name_1, '-n', name_2]
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            self.path = fout.name
        text = self.chain_objects.make_chain_from_binary_file(self.entry_credit_address1000, self.path,
                                                              external_id_list=chain_names_list)
        chain_dict = self.chain_objects.parse_simple_data(text)
        chain_id = chain_dict['ChainID']

        # compose entry by chain id
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        entry_names_list = ['-c', chain_id] + ['-e', name_1, '-e', name_2]
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            self.path = fout.name
        self.assertTrue("message" and "entry" in self.chain_objects.compose_entry_from_binary_file(
            self.entry_credit_address1000, self.path, external_id_list=entry_names_list))

        # compose entry by external id
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        entry_names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            self.path = fout.name
        self.assertTrue("message" and "entry" in self.chain_objects.compose_entry_from_binary_file(self.entry_credit_address1000, self.path, external_id_list=entry_names_list))

        # force compose entry by hex external id
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        factom_flags_list = ['-f']
        entry_names_list = chain_names_list + ['-x', name_1, '-x', name_2]
        with open('output_file', 'wb') as fout:
            fout.write(os.urandom(10))
            self.path = fout.name
        self.assertTrue("message" and "entry" in self.chain_objects.compose_entry_from_binary_file(self.entry_credit_address1000, self.path, external_id_list=entry_names_list, flag_list=factom_flags_list))
