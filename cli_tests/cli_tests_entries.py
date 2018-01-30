import unittest
import os, binascii, hashlib, time

from flaky import flaky

from nose.plugins.attrib import attr
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address
from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain

@flaky(max_runs=3, min_passes=1)
@attr(fast=True)
class CLITestsEntries(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.cli_chain = CLIObjectsChain()
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_credit_address1000 = fund_entry_credit_address(1000)
        self.blocktime = int(os.environ['BLOCKTIME'])

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
        factom_flags_list = ['-E']
        entry_hash = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000, data, external_id_list=names_list, flag_list=factom_flags_list)
        self.assertNotIn("Entry not found", self.cli_chain.get_entry_by_hash(entry_hash),
                        "Entry not revealed")

    def test_raw_entry(self):
        # make chain
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        factom_flags_list = ['-E']
        entry_hash = self.cli_chain.make_chain(self.entry_credit_address1000, data, external_id_list=names_list, flag_list=factom_flags_list)
        raw = self.cli_create.get_raw(entry_hash)

        # convert to binary
        serialized_raw = binascii.unhexlify(raw)

        # hash via SHA512
        hashed512_raw = hashlib.sha512(serialized_raw).digest()

        # concatenate SHA512 hash binary result and serialized raw data
        prepended_raw = hashed512_raw + serialized_raw

        # hash via SHA256 the concatenated data
        hashed256_raw = hashlib.sha256(prepended_raw).hexdigest()

        self.assertEqual(hashed256_raw, entry_hash, 'Raw data string is not correct')

    @attr(fast=False)
    def test_verify_entry_costs(self):
        ONE_K_MINUS_8 = 1016
        '''
        entry cost = 1 ec per 1024 bytes
        overhead = total length of external ids + 2 bytes per external id
        There are 2 external ids of 2 bytes each
        1024 - 4(2 external ids x 2 bytes length) - 4(2 bytes x 2 external ids) = 1016
        '''

        MAX_ENTRY_SIZE_MINUS_7 = 10233
        '''
        largest allowable entry is 10K = 10240 bytes
        smallest too large entry = 10241 bytes
        10241 - 4(2 external ids x 2 bytes length) - 4(2 bytes x 2 external id) = 10233
        '''

        # create chain
        chain_name_1 = create_random_string(5)
        chain_name_2 = create_random_string(5)
        chain_names_list = ['-n', chain_name_1, '-n', chain_name_2]
        firstentry_ext_id = chain_name_1

        i = ONE_K_MINUS_8
        data = create_random_string(i)
        text = self.cli_chain.make_chain(self.entry_credit_address1000, data, external_id_list=chain_names_list)
        chain_dict = self.cli_chain.parse_simple_data(text)
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
            text = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000,
                                                     data, external_id_list=names_list)
            tx_id = self.cli_chain.parse_simple_data(text)['CommitTxID']
            wait_for_ack(tx_id)
            balance_last = self.cli_create.check_wallet_address_balance(self.entry_credit_address1000)
            self.assertEqual(int(balance_1st), int(balance_last) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            # write smallest entry for fee amount
            i += 1
            data = create_random_string(i)
            if i == MAX_ENTRY_SIZE_MINUS_7: break
            name_1 = binascii.b2a_hex(os.urandom(2))
            name_2 = binascii.b2a_hex(os.urandom(2))
            names_list = ['-c', chain_id, '-x', name_1, '-x', name_2]
            text = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000,
                                                     data, external_id_list=names_list)
            tx_id = self.cli_chain.parse_simple_data(text)['CommitTxID']
            wait_for_ack(tx_id)
            balance_1st = self.cli_create.check_wallet_address_balance(self.entry_credit_address1000)
            self.assertEqual(int(balance_last), int(balance_1st) + (i + 7) / 1024 + 1, 'Incorrect charge for entry')

            i += 1023
            data = create_random_string(i)

        # write too large entry
        name_1 = create_random_string(2)
        name_2 = create_random_string(2)
        names_list = ['-c', chain_id, '-e', name_1, '-e', name_2]

        self.assertIn("Entry cannot be larger than 10KB", self.cli_chain.add_entry_to_chain(self.entry_credit_address1000, data, external_id_list=names_list))

        # check for pending entries
        for x in range(0, self.blocktime+1):
            chain = self.cli_chain.get_pending_entries()
            if (chain and not chain.isspace()): break
            else: time.sleep(1)
        self.assertLess(x, self.blocktime, 'Chain ' + chain_id + ' never pending')
        self.assertIn(chain_id, chain, 'Chain not shown as pending')

        # validate get firstentry command
        wait_for_chain_in_block(external_id_list=chain_names_list)
        self.assertIn("ExtID: " + firstentry_ext_id, self.cli_chain.get_firstentry(external_id_list=chain_names_list), 'Chain not found')

        # validate get firstentry_return_entry_hash
        factom_flags_list = ['-E']
        entry_hash = self.cli_chain.get_firstentry(flag_list=factom_flags_list, chain_id=chain_id)
        self.assertTrue(entry_hash and "Entry [0]" in self.cli_chain.get_allentries(chain_id=chain_id),
                        'Entry not found')

    def test_force_make_entry_with_hex_external_chain_id(self):
        # make chain
        data = create_random_string(1024)
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        chain_names_list = ['-h', name_1, '-h', name_2]
        text = self.cli_chain.make_chain(self.entry_credit_address1000, data, external_id_list=chain_names_list)
        chain_id = self.cli_chain.parse_simple_data(text)['ChainID']
        entry_hash = self.cli_chain.parse_simple_data(text)['Entryhash']

        # make entry
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-f', '-T']
        tx_id = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000,                                      data, external_id_list=names_list, flag_list=factom_flags_list)

        # check for pending entries return entry hash
        factom_flags_list = ['-E']
        for x in range(0, self.blocktime+1):
            pending_list = self.cli_chain.get_pending_entries(flag_list=factom_flags_list)
            if (pending_list and not pending_list.isspace()): break
            else: time.sleep(1)
        self.assertLess(x, self.blocktime, 'Entry ' + str(names_list) + ' never pending')
        found = False
        for pending in pending_list.split('\n'):
            text = self.cli_chain.get_entry_by_hash(pending)
            print 'text', text
            self.assertNotIn('Invalid', text,'Entry Hash is invalid')
            entry_chain_id = self.cli_chain.parse_entry_data(text)['ChainID']
            if entry_chain_id == chain_id:
               found = True
               break
        self.assertTrue(found, 'Entry not shown as pending')

        wait_for_ack(tx_id)
        self.assertIn("TransactionACK", self.cli_create.request_transaction_acknowledgement(tx_id),
                        "Forced entry was not revealed")

        # compose entry by external chain id
        self.assertTrue(
            "message" and "entry" in self.cli_chain.compose_entry(self.entry_credit_address1000, data, external_id_list=names_list))
        # wait for entry to arrive in block
        wait_for_chain_in_block(external_id_list=chain_names_list)

        # look for chainhead by hex external id
        text = self.cli_chain.get_chainhead(external_id_list=chain_names_list)
        self.assertIn('PrevKeyMR: 0000000000000000000000000000000000000000000000000000000000000000', text, 'Chainhead not found')

        # look for chainhead by hex external id return KeyMR
        keyMR = self.cli_chain.parse_block_data(text)['EBlock']
        factom_flags_list = ['-K']
        self.assertEqual(keyMR, self.cli_chain.get_chainhead(external_id_list=chain_names_list, flag_list=factom_flags_list), 'Key merkle root does not match')

        # check get allentries by hex external id
        factom_flags_list = [' -E']
        self.assertIn(entry_hash, self.cli_chain.get_allentries(flag_list=factom_flags_list, external_id_list=chain_names_list), 'Chain not found')

    def test_quiet_make_entry(self):
        '''
        This test is only reliable on the 1st run on a given database.
          Because of the -q flag, no transaction id is available, so the only way to locate the created entry is by
          using a fixed entry in a fixed chain id which yields a known entry hash. However once this entry is created
          in a database, it will still be there even if subsequent runs fail.
        '''

        # make chain
        content = 'x'*1024
        name_1 = self.data['2nd_external_id1']
        name_2 = self.data['2nd_external_id2']
        chain_names_list = ['-n', name_1, '-n', name_2]
        self.cli_chain.make_chain(self.entry_credit_address1000, content, external_id_list=chain_names_list)

        # make entry
        content = 'y'*1024
        name_1 = self.data['3rd_over_2nd_external_id1']
        name_2 = self.data['3rd_over_2nd_external_id2']
        entry_names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        factom_flags_list = ['-q']
        self.cli_chain.add_entry_to_chain(self.entry_credit_address1000, content, external_id_list=entry_names_list, flag_list=factom_flags_list)

        # wait for entry to arrive in block
        wait_for_chain_in_block(external_id_list=chain_names_list)

        self.assertNotIn("Entry not found", self.cli_chain.get_entry_by_hash(self.data['3rd_over_2nd_entry_hash']))

        # check get allentries by external id and returning entry hash
        factom_flags_list = ['-E']
        self.assertIn(self.data['3rd_over_2nd_entry_hash'], self.cli_chain.get_allentries(external_id_list=chain_names_list, flag_list=factom_flags_list), "Entry not found")

    def test_make_entry_return_chain_id(self):

        # make chain
        content = create_random_string(1024)
        chain_name_1 = create_random_string(5)
        chain_name_2 = create_random_string(5)
        chain_names_list = ['-n', chain_name_1, '-n', chain_name_2]
        factom_flags_list = ['-C']
        chain_id = self.cli_chain.make_chain(self.entry_credit_address1000, content, external_id_list=chain_names_list, flag_list=factom_flags_list)

        # make entry
        content = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        entry_names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        entry_chain_id = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000, content, external_id_list=entry_names_list, flag_list=factom_flags_list)

        # wait for entry to arrive in block
        wait_for_chain_in_block(external_id_list=chain_names_list)

        self.assertEqual(entry_chain_id, chain_id, 'Chain Id of Entry does not match Chain ID of chain')
        self.assertIn(entry_chain_id, self.cli_chain.get_allentries(chain_id=chain_id), "Entry not found")

        # look for chainhead by chain id
        self.assertIn('ChainID: ' + entry_chain_id, self.cli_chain.get_chainhead(chain_id=chain_id), 'Chainhead not found')

    def test_compose_entry(self):
        # make chain
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        chain_names_list = ['-n', name_1, '-n', name_2]
        content = create_random_string(10)
        text = self.cli_chain.make_chain(self.entry_credit_address1000, content,
                                         external_id_list=chain_names_list)
        chain_dict = self.cli_chain.parse_simple_data(text)
        chain_id = chain_dict['ChainID']

        # compose entry by chain id
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        entry_names_list = ['-c', chain_id] + ['-e', name_1, '-e', name_2]
        content = create_random_string(10)
        self.assertTrue("message" and "entry" in self.cli_chain.compose_entry(
            self.entry_credit_address1000, content, external_id_list=entry_names_list))

        # compose entry by external id
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        entry_names_list = chain_names_list + ['-e', name_1, '-e', name_2]
        content = create_random_string(1024)
        self.assertTrue("message" and "entry" in self.cli_chain.compose_entry(self.entry_credit_address1000, content, external_id_list=entry_names_list))

        # force compose entry by hex external id
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        factom_flags_list = ['-f']
        entry_names_list = chain_names_list + ['-x', name_1, '-x', name_2]
        content = create_random_string(1024)
        self.assertTrue("message" and "entry" in self.cli_chain.compose_entry(self.entry_credit_address1000, content, external_id_list=entry_names_list, flag_list=factom_flags_list))
