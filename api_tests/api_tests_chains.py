import unittest
import os, binascii

from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_entry_in_block, fund_entry_credit_address
from helpers.api_methods import generate_random_external_ids_and_content
from nose.plugins.attrib import attr

@attr(api=True)
class APIChainsTests(unittest.TestCase):

    def setUp(self):
        self.api_objects_factomd = APIObjectsFactomd()
        self.api_objects_wallet = APIObjectsWallet()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_commit_chain(self):
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        # message, entry = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)
        compose, error_message = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)
        if not error_message:

            # commit chain
            commit_response, commit_success  = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            if not commit_success:
                fail_message, info, entryhash = self.__commit_failure_data(commit_response)
                self.assertTrue(False, 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)

    def test_repeated_commits(self):
        balance_before = self.api_objects_factomd.get_entry_credits_balance(self.entry_credit_address1000)
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose, error_message = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)
        if not error_message:

            # commit chain
            commit_response, commit_success  = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            if not commit_success:
                fail_message, info, entryhash = self.__commit_failure_data(commit_response)
                self.assertNotIn('Repeated Commit', fail_message,
                                 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)
                # failed for some other reason
                self.assertTrue(False, 'Chain commit failed - ' + fail_message)
            else:
                # wait for 1st commit to be acknowledged
                tx_id = commit_response['txid']
                wait_for_ack(tx_id)

            # try to repeat commit
            commit_response, commit_success  = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])

            if commit_success:
                self.assertFalse(True, 'Repeated commit allowed - entryhash ' + str(commit_response['entryhash']))
            else:
                fail_message, info, entryhash = self.__commit_failure_data(commit_response)
                self.assertIn('Repeated Commit', fail_message, 'Chain commit failed because of - ' + fail_message + ' - ' + info + ' instead of Repeated Commit - entryhash ' + entryhash)

            # see if 2nd commit has been mistakenly paid for
            wait_for_entry_in_block(external_id_list=chain_external_ids)
            balance_after = self.api_objects_factomd.get_entry_credits_balance(self.entry_credit_address1000)
            self.assertEqual(balance_before, balance_after + 12, 'Balance before commit = ' + str(balance_before) + '. Balance after commit = ' + str(balance_after) + '. Balance after single commit SHOULD be = ' + str(balance_after + 12))

    def __commit_failure_data(self, commit_response):
        message = str(commit_response['message'])
        info = str(commit_response['data']['info'])
        entryhash = str(commit_response['data']['entryhash'])
        return message, info, entryhash

    def test_reveal_chain(self):
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose, error_message = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)
        if not error_message:

            # commit chain
            commit_response, commit_success  = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            if not commit_success:
                fail_message, info, entryhash = self.__commit_failure_data(commit_response)
                self.assertNotIn('Repeated Commit', fail_message,
                                 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)
                # failed for some other reason
                self.assertTrue(False, 'Chain commit failed - ' + fail_message)
            else:

                # reveal_chain
                reveal_response, reveal_success  = self.api_objects_factomd.reveal_chain(compose['reveal']['params']['entry'])
                if not reveal_success:
                    fail_message = str(reveal_response['message'])
                    data = str(reveal_response['data'])
                    self.assertTrue(False,
                                    'Chain reveal failed - ' + fail_message + ' - ' + data)

