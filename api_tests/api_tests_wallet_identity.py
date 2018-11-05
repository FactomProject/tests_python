import unittest, string, random, time

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address, wait_for_chain_in_block, wait_for_entry_in_block
from helpers.api_methods import generate_random_external_ids_and_content

@attr(fast=True)
class ApiTestsWallet(unittest.TestCase):
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    WAITTIME = 300
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        public_keys = self.api_wallet.import_addresses(
            self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        self.first_address = public_keys[0]
        self.entry_creds_wallet = public_keys[1]
        self.second_address = self.api_wallet.generate_factoid_address()
        self.entry_creds_wallet2 = self.api_wallet.generate_ec_address()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)


    def test_identity_key(self):
        keys = self.api_wallet.generate_identity_key()
        result =  self.api_wallet.identity_key(keys['public'])
        if result['secret'] == keys['secret']:
            print "keys matched"


    def test_all_identity_keys(self):
        result = self.api_wallet.all_identity_keys()
        print result


    def test_remove_identity_keys(self):
        #generate identity key
        keys = self.api_wallet.generate_identity_key()

        #remove the generated key
        self.api_wallet.remove_identity_keys(keys['public'])

        #list all the identity key
        identity_list = self.api_wallet.all_identity_keys()

        #flag to confirm the key is found
        found = False

        #check if the check is found in the list of identity keys. pass if not found. fail if found.
        for i in range(0,len(identity_list['keys'])):
            if identity_list['keys'][i]['public'] == keys['public']:
                found = True

        if found == False:
            print "Remove Identity Key Passed"
        else:
            print "Remove Identity Key Failed"


    def test_compose_identity_chain(self):

        chain_external_ids, content = generate_random_external_ids_and_content()
        keylist = []
        # generate 5 identities to be added as identity chain content
        for i in range(0, 5):
            keylist.append(self.api_wallet.generate_identity_key()['public'])

        # compose identity chain
        compose = self.api_wallet.compose_identity_chain(chain_external_ids, keylist, self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])


    def test_compose_identity_chain_max_size(self):

        chain_external_ids, content = generate_random_external_ids_and_content()
        keylist = []
        #each identity is 55 bytes. 170 identities creates 10KB of chain content
        for i in range(0,170):
            keylist.append(self.api_wallet.generate_identity_key()['public'])

        # compose identity chain
        compose = self.api_wallet.compose_identity_chain(chain_external_ids,keylist,self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])


    def test_identity_key_at_height(self):

        chain_external_ids, content = generate_random_external_ids_and_content()
        keylist = []

        # generate 5 identities to be added as identity chain content
        for i in range(0, 5):
            keylist.append(self.api_wallet.generate_identity_key()['public'])

        # compose identity chain
        compose = self.api_wallet.compose_identity_chain(chain_external_ids, keylist, self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])
        print reveal['chainid']
        status = wait_for_chain_in_block(external_id_list=chain_external_ids)
        print status
        time.sleep(30)

        height = self.api_factomd.get_heights()

        print self.api_wallet.identity_key_at_height(reveal['chainid'], height['directoryblockheight'])


    def test_compose_key_replacement(self):
        chain_external_ids, content = generate_random_external_ids_and_content()
        keylist = []
        # generate 5 identities to be added as identity chain content
        for i in range(0, 5):
            keylist.append(self.api_wallet.generate_identity_key()['public'])

        # compose identity chain
        compose = self.api_wallet.compose_identity_chain(chain_external_ids, keylist, self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])

        #wait until chain is written into the blockchain
        chain_external_ids.insert(0, '-h')
        chain_external_ids.insert(2, '-h')

        status = wait_for_chain_in_block(external_id_list=chain_external_ids)

        #generate a new key to replace one of the old keys
        newkey = self.api_wallet.generate_identity_key()

        #compose entry with the new key
        compose_entry = self.api_wallet.compose_identity_key_replacement(reveal['chainid'],keylist[3],newkey['public'],keylist[0],self.entry_credit_address1000,True)

        # commit entry
        commit_entry = self.api_factomd.commit_entry(compose_entry['commit']['params']['message'])

        # reveal entry
        reveal_entry = self.api_factomd.reveal_entry(compose_entry['reveal']['params']['entry'])

        # check if entry arrived in block
        status = wait_for_entry_in_block(reveal_entry['entryhash'], reveal_entry['chainid'])

        self.assertIn('DBlockConfirmed',
                      str(self.api_factomd.get_status(reveal['entryhash'], reveal['chainid'])), 'Entry not arrived in block')

        # look for entry by hash
        self.assertIn(reveal['chainid'], str(self.api_factomd.get_entry_by_hash(reveal['entryhash'])), 'Entry with entryhash ' + reveal['entryhash'] + ' not found')

        #get the current height
        height = self.api_factomd.get_heights()

        #get the identity keys of the chain
        result = self.api_wallet.identity_key_at_height(reveal['chainid'], height['directoryblockheight'])

        #compare the identity keys before replacing and after replacing. If they are same then test case failed else test case passed
        if keylist != result['keys']:
            print "keys are not matching"
        else:
            print "keys matched"


    def compose_attribute(self):
        #create destination chain
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose identity chain
        compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])

        destination_chainid = reveal['chainid']

        # wait until chain is written into the blockchain
        chain_external_ids.insert(0, '-h')
        chain_external_ids.insert(2, '-h')

        status = wait_for_chain_in_block(external_id_list=chain_external_ids)


        #create receiver chain

        chain_external_ids, content = generate_random_external_ids_and_content()
        keylist = []
        # generate 5 identities to be added as identity chain content
        for i in range(0, 5):
            keylist.append(self.api_wallet.generate_identity_key()['public'])

        # compose identity chain
        compose = self.api_wallet.compose_identity_chain(chain_external_ids, keylist, self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])

        receiver_chainid= reveal['chainid']

        # wait until chain is written into the blockchain
        chain_external_ids.insert(0, '-h')
        chain_external_ids.insert(2, '-h')

        status = wait_for_chain_in_block(external_id_list=chain_external_ids)

        #compose chain to create new identity attribute entry
        attributes = [{"key":"email","value":"veena@abc.com"}]
        signerkey = keylist[0]
        signer_chainid =  receiver_chainid

        compose = self.api_wallet.compose_identity_attribute(receiver_chainid,destination_chainid,attributes,signer_chainid,signerkey,self.entry_credit_address1000)
        # commit entry
        commit = self.api_factomd.commit_entry(compose['commit']['params']['message'])

        # reveal entry
        reveal = self.api_factomd.reveal_entry(compose['reveal']['params']['entry'])

        status = wait_for_entry_in_block(reveal['entryhash'], reveal['chainid'])

        return reveal['entryhash'], reveal['chainid'], receiver_chainid


    def test_compose_attribute(self):

        entry_hash, chainid, receiver_chainid = self.compose_attribute()
        self.assertIn('DBlockConfirmed', str(self.api_factomd.get_status(entry_hash,chainid)), 'Entry not arrived in block')


    def test_compose_attribute_endorsement(self):
        entry_hash,chainid, receiver_chainid = self.compose_attribute()

        # get the current height
        height = self.api_factomd.get_heights()

        # get the identity keys of the chain
        result = self.api_wallet.identity_key_at_height(receiver_chainid, height['directoryblockheight'])
        signer_key = result['keys'][0]

        #compose entry for attribute endorsement
        compose = self.api_wallet.compose_identity_attribute_endorsement(receiver_chainid,entry_hash,signer_key,chainid,self.entry_credit_address1000)

        # commit entry

        commit = self.api_factomd.commit_entry(compose['commit']['params']['message'])

        # reveal entry
        reveal = self.api_factomd.reveal_entry(compose['reveal']['params']['entry'])

        status = wait_for_entry_in_block(reveal['entryhash'], reveal['chainid'])
        self.assertIn('DBlockConfirmed', str(self.api_factomd.get_status(reveal['entryhash'], reveal['chainid'])),
                      'Entry not arrived in block')