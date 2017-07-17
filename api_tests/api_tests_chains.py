import unittest
import os, binascii

from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_entry_in_block, fund_entry_credit_address
from nose.plugins.attrib import attr

@attr(api=True)
class APIEntriesTests(unittest.TestCase):

    def setUp(self):
        self.factom_api = APIObjectsFactomd()
        self.wallet_api_objects = APIObjectsWallet()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_make_entry(self):

        # external ids must be in hex
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
        with open(path, 'r') as fin:
            content = binascii.hexlify(fin.read())

        # compose chain
        message, entry = self.wallet_api_objects.compose_chain(external_ids, content, self.entry_credit_address1000)
        balance_before = self.factom_api.get_entry_credits_balance_by_ec_address(self.entry_credit_address1000)

        # commit chain
        commit_success, commit_response = self.factom_api.commit_chain_by_message(message)

        if not commit_success:
            self.assertNotIn('Repeated Commit', commit_response['message'], 'Chain commit failed - ' + str(commit_response['message']) + ' - ' + str(commit_response['data']['info']) +              ' - entryhash ' + str(commit_response['data']['entryhash']))
            # failed for some other reason
            self.assertTrue(False, 'Chain commit failed - ' + str(commit_response['message']))
        else:
            tx_id = commit_response['txid']
            wait_for_ack(tx_id)

        # try to repeat commit after 1st one acknowledged
        commit_success, commit_response = self.factom_api.commit_chain_by_message(message)

        if commit_success:
            self.assertFalse(True, 'Repeated commit allowed - entryhash ' + str(commit_response['entryhash']))
        else:
            self.assertIn('Repeated Commit', commit_response['message'], 'Chain commit failed because of - ' + str(commit_response['message']) + ' - ' + str(commit_response['data']['info']) +              ' instead of Repeated Commit - entryhash ' + str(commit_response['data']['entryhash']))

        # see if 2nd commit has been paid for
        wait_for_entry_in_block(external_id_list=external_ids)
        balance_after = self.factom_api.get_entry_credits_balance_by_ec_address(self.entry_credit_address1000)
        self.assertEqual(balance_before, balance_after + 12, 'Commit paid for twice')
