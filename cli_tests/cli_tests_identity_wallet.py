import unittest, os, binascii, time

from helpers.helpers import create_random_string

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_identity_wallet import CLIObjectsIdentityWallet
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address, wait_for_entry_in_block

@attr(fast=True)
class CLITestsChains(unittest.TestCase):
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    cli_identity = CLIObjectsIdentityWallet()
    api_factomd = APIObjectsFactomd()
    data = read_data_from_json('shared_test_data.json')
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']

    TIME_TO_WAIT = 5


    def test_list_all_identity_keys(self):
        newkey = self.cli_identity.new_identity_key()
        found = False
        keylist =  (self.cli_identity.list_identity_keys()).split()
        for i in range(0, len(keylist)-1):
            if newkey == keylist[i]:
                found = True
                break
        self.assertTrue(found, "Testcase Failed")

    def test_rm_identity_keys(self):
        newkey = self.cli_identity.new_identity_key()
        found = False
        self.cli_identity.rm_identity_key(newkey)

        keylist = (self.cli_identity.list_identity_keys()).split()

        for i in range(0, len(keylist) - 1):
            if newkey == keylist[i]:
                found = True
                break
        self.assertFalse(found, "Testcase Failed")

    def test_make_chain_and_check_chainhead(self):
        chainid = self.compose_identity_chain()
        self.confirm_chain_in_blockchain(chainid)

    def compose_identity_chain(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-f', '-C']
        key1 = self.cli_identity.new_identity_key()
        key2 = self.cli_identity.new_identity_key()
        key3 = self.cli_identity.new_identity_key()
        key_list = ['-k',key1,'-k', key2, '-k', key3]


        chainid = self.cli_identity.add_identity_chain(self.entry_credit_address100, data, flag_list= chain_flag_list, external_id_list=names_list,
                                            public_key_list=key_list)
        return chainid

    def make_chain(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-f', '-C']
        chainid = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)
        return chainid

    def confirm_chain_in_blockchain(self,chainid):
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

    def test_compose_attribute(self):
        '''
        Create a new Identity Attribute Entry using the Entry Credits from the specified address. Optional output flags: -C ChainID. -E EntryHash. -T TxID.
        '''
        chainid =  self.make_chain()
        self.confirm_chain_in_blockchain(chainid)
        receiver_chainid = self.compose_identity_chain()
        self.confirm_chain_in_blockchain(receiver_chainid)
        self.entry_credit_address100 = fund_entry_credit_address(100)
        self.heights =  self.cli_chain.get_heights()
        directory_block_height = self.cli_chain.parse_transaction_data(self.heights)['DirectoryBlockHeight']
        self.keys = self.cli_identity.get_keys_at_height(receiver_chainid,directory_block_height)
        signerkey = self.cli_chain.parse_keys_data(self.keys,0)
        signer_chainid = receiver_chainid
        attributes = "\'[{\"key\": \"email\", \"value\": \"veena@abc.com\"}]\'"

        entry_text = self.cli_identity.add_attribute(chainid, receiver_chainid, signer_chainid, signerkey, attributes, self.entry_credit_address100)
        entry_text = entry_text.split('\n')
        entry_hash = ((entry_text[-1]).split(": "))[1]
        wait_for_entry_in_block(entry_hash,chainid)

        self.assertIn('DBlockConfirmed',
                      str(self.api_factomd.get_status(entry_hash,chainid)),
                      'Entry not arrived in block')

    def test_compose_attribute_endorsement(self):
        '''
        Create a new Endorsement Entry for the Identity Attribute at the given entry hash. Uses the Entry Credits from the specified address. Optional output flags: -C ChainID. -E EntryHash. -T TxID.
        '''

        #compose attribute
        chainid =  self.make_chain()
        self.confirm_chain_in_blockchain(chainid)
        receiver_chainid = self.compose_identity_chain()
        self.confirm_chain_in_blockchain(receiver_chainid)
        self.entry_credit_address100 = fund_entry_credit_address(100)
        self.heights =  self.cli_chain.get_heights()
        directory_block_height = self.cli_chain.parse_transaction_data(self.heights)['DirectoryBlockHeight']
        self.keys = self.cli_identity.get_keys_at_height(receiver_chainid,directory_block_height)
        signerkey = self.cli_chain.parse_keys_data(self.keys,0)
        signer_chainid = receiver_chainid
        attributes = "\'[{\"key\": \"email\", \"value\": \"veena@abc.com\"}]\'"

        entry_text = self.cli_identity.add_attribute(chainid, receiver_chainid, signer_chainid, signerkey, attributes, self.entry_credit_address100)
        entry_text = entry_text.split('\n')
        entry_hash = ((entry_text[-1]).split(": "))[1]

        #compose attribute endorsement
        entry_text = self.cli_identity.add_attribute_endorsement(chainid,signer_chainid,signerkey,entry_hash,self.entry_credit_address100)
        entry_text = entry_text.split('\n')
        entry_hash = ((entry_text[-1]).split(": "))[1]
        wait_for_entry_in_block(entry_hash,chainid)
        self.assertIn('DBlockConfirmed',
                      str(self.api_factomd.get_status(entry_hash,chainid)),
                      'Entry not arrived in block')

    def test_key_replacement(self):
        '''
        Create a new Identity Key Replacement Entry using the Entry Credits from the specified address. The oldkey is replaced by the newkey, and signerkey (same or higher priority as oldkey) authorizes the replacement. Optional output flags: -C ChainID. -E EntryHash. -T TxID.
        :return:
        '''

        # compose identity
        chainid = self.compose_identity_chain()
        self.confirm_chain_in_blockchain(chainid)

        # inputs for cli add key replacement
        # fetch the height and keys of the chain id
        self.heights =  self.cli_chain.get_heights()
        directory_block_height = self.cli_chain.parse_transaction_data(self.heights)['DirectoryBlockHeight']
        keys = self.cli_identity.get_keys_at_height(chainid,directory_block_height)
        signerkey = self.cli_chain.parse_keys_data(keys,0)
        oldkey = self.cli_chain.parse_keys_data(keys,2)

        self.entry_credit_address100 = fund_entry_credit_address(100)
        newkey = self.cli_identity.new_identity_key()

        # identity add key replacement
        entry_text = self.cli_identity.add_key_replacement(chainid,oldkey,newkey,signerkey,self.entry_credit_address100)
        entry_text = entry_text.split('\n')
        entry_hash = ((entry_text[-1]).split(": "))[1]
        wait_for_entry_in_block(entry_hash,chainid)

        # fetch the height and keys of the chain id
        heights = self.cli_chain.get_heights()
        directory_block_height = self.cli_chain.parse_transaction_data(heights)['DirectoryBlockHeight']
        new_key_list = self.cli_identity.get_keys_at_height(chainid, directory_block_height)

        # fetch the key list and add it to the parsed key list
        parsed_key_list = []
        for i in range(0,3):
            parsed_key_list.append(self.cli_chain.parse_keys_data(new_key_list,i))

        #look for that new key in the new key list
        found = False
        for i in range(0,len(parsed_key_list)):
            if (str(parsed_key_list[i]) == str(newkey)):
                found = True
                break

        self.assertTrue(found, "Testcase Failed")
