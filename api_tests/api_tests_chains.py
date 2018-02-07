import unittest, binascii, os, json

from nose.plugins.attrib import attr
from helpers.helpers import read_data_from_json, create_random_string
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address
from helpers.api_methods import generate_random_external_ids_and_content
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet

@attr(api=True)
@attr(fast=True)
class APIChainsTests(unittest.TestCase):

    def setUp(self):
        self.api_objects_factomd = APIObjectsFactomd()
        self.api_objects_wallet = APIObjectsWallet()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_compose_commit_reveal_chain(self):
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)

        # commit chain
        commit = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal  = self.api_objects_factomd.reveal_chain(compose['reveal']['params']['entry'])

        # search for revealed chain
        chain_external_ids.insert(0, '-h')
        chain_external_ids.insert(2, '-h')
        status = wait_for_chain_in_block(external_id_list=chain_external_ids)

        # chain's existence is acknowledged?
        self.assertNotIn('Missing Chain Head', status, 'Chain not revealed')

        # chain arrived in block?
        self.assertTrue('DBlockConfirmed' in str(self.api_objects_factomd.get_status(reveal['entryhash'], reveal['chainid'])), 'Chain not arrived in block')

    def test_repeated_commits(self):
        balance_before = self.api_objects_factomd.get_entry_credit_balance(self.entry_credit_address1000)

        # commit chain
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)

        # commit chain
        commit = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])

        # wait for 1st commit to be acknowledged
        tx_id = commit['txid']
        wait_for_ack(tx_id)

        # try to repeat commit
        allow_fail = True
        block = json.loads(self.api_objects_factomd.send_get_request_with_params_dict('commit-chain', {'message': compose['commit']['params']['message']}, allow_fail))

        if 'Repeated Commit' not in str(block):

            # repeated chain commit wrongly allowed
            if 'error' in str(block):

                # repeated chain commit failed for a different reason
                exit('Chain commit of entryhash ' + str(commit['entryhash']) + ' failed - ' + str(block['error']))
            else:

                # see if 2nd commit has been mistakenly paid for
                chain_external_ids.insert(0, '-h')
                chain_external_ids.insert(2, '-h')
                wait_for_chain_in_block(external_id_list=chain_external_ids)
                balance_after = self.api_objects_factomd.get_entry_credit_balance(self.entry_credit_address1000)
                self.assertEqual(balance_before, balance_after + 12, 'Balance before commit = ' + str(balance_before) + '. Balance after commit = ' + str(balance_after) + '. Balance after single commit SHOULD be = ' + str(balance_after + 12))
                exit('Repeated commit allowed for entryhash ' + str(commit['entryhash']))

    def test_raw_message(self):
        external_ids, content = generate_random_external_ids_and_content()
        print 'external_ids', external_ids
        print 'content', content
        compose = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)
        prefix = '0d'
        timestamp = compose['commit']['params']['message'][2:14]
        entry = compose['reveal']['params']['entry']
        raw_message = prefix + timestamp + entry
        self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
        self.api_objects_factomd.send_raw_message(raw_message)

    def __failure_data(self, commit_response):
        message = str(commit_response['message'])
        info = str(commit_response['data']['info'])
        entryhash = str(commit_response['data']['entryhash'])
        return message, info, entryhash
