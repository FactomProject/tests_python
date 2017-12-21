import unittest, binascii, os

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
        self.entry_credit_address1000 = fund_entry_credit_address(1000)[0]

    @unittest.expectedFailure
    # TODO remove expectedFailure tag once commit_chain function is fixed so that it actually creates the requested chain instead of trying to create the null chain
    def test_compose_commit_reveal_chain(self):
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose, compose_error = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)
        self.assertFalse(compose_error,'Compose chain failed because ' + compose_error)

        # commit chain
        external_ids, content = self.__random_chain()
        compose, error_message = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)
        if error_message:
            self.assertFalse(True, 'Chain compose failed - ' + error_message)
        else:
            commit, error_message = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            if error_message:
                fail_message, info, entryhash = self.__failure_data(commit)
                self.assertTrue(False, 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)
            else:
                # reveal chain
                reveal, reveal_error  = self.api_objects_factomd.reveal_chain(compose['reveal']['params']['entry'])
                if reveal_error:
                    fail_message = str(reveal['message'])
                    data = str(reveal['data'])
                    self.assertTrue(False, 'Chain reveal failed - ' + fail_message + ' - ' + data)
                else:
                    # recreate external id parameter from external id list
                    chain_external_ids.insert(0, '-h')
                    chain_external_ids.insert(2, '-h')

                    # search for revealed chain
                    status = wait_for_chain_in_block(external_id_list=chain_external_ids)

                    # chain's existence is acknowledged?
                    self.assertNotIn('Missing Chain Head', status, 'Chain not revealed')

                    # chain arrived in block?
                    self.assertTrue('DBlockConfirmed' in str(self.api_objects_factomd.get_status(reveal['entryhash'], reveal['chainid'])), 'Chain not arrived in block')

    def test_repeated_commits(self):
        balance_before = self.api_objects_factomd.get_entry_credit_balance(self.entry_credit_address1000)[0]['balance']

        # commit chain
        external_ids, content = self.__random_chain()
        compose, error_message = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)
        if error_message:
            self.assertFalse(True, 'Chain compose failed - ' + error_message)
        else:
            commit, error_message = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            if error_message:
                fail_message, info, entryhash = self.__failure_data(commit)
                self.assertNotIn('Repeated Commit', fail_message,
                                 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)
            # failed for some other reason
                self.assertTrue(False, 'Chain commit failed - ' + fail_message)
            else:
                # wait for 1st commit to be acknowledged
                tx_id = commit['txid']
                wait_for_ack(tx_id)

                # try to repeat commit
                commit, error_message = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
                if error_message:
                    fail_message, info, entryhash = self.__failure_data(commit)
                    self.assertIn('Repeated Commit', fail_message, 'Chain commit failed because of - ' + fail_message + ' - ' + info + ' instead of Repeated Commit - entryhash ' + entryhash)
                else:
                    self.assertFalse(True, 'Repeated commit allowed - entryhash ' + str(commit['entryhash']))

                # see if 2nd commit has been mistakenly paid for
                wait_for_chain_in_block(external_id_list=external_ids)
                balance_after = self.api_objects_factomd.get_entry_credit_balance(self.entry_credit_address1000)[0]['balance']
                self.assertEqual(balance_before, balance_after + 12, 'Balance before commit = ' + str(balance_before) + '. Balance after commit = ' + str(balance_after) + '. Balance after single commit SHOULD be = ' + str(balance_after + 12))

    def test_raw_message(self):
        external_ids, content = self.__random_chain()
        print 'external_ids', external_ids
        print 'content', content
        compose, error_message = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)
        if error_message:
            self.assertFalse(True, 'Chain compose failed - ' + error_message)
        else:
            prefix = '0d'
            timestamp = compose['commit']['params']['message'][2:14]
            entry = compose['reveal']['params']['entry']
            raw_message = prefix + timestamp + entry
            commit, error_message = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            if error_message:
                fail_message, info, entryhash = self.__failure_data(commit)
                self.assertNotIn('Repeated Commit', fail_message,
                                 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)
            # failed for some other reason
                self.assertTrue(False, 'Chain commit failed - ' + fail_message)
            else:
                raw, error_message = self.api_objects_factomd.send_raw_message(raw_message)
                if error_message:
                    self.assertFalse(True, 'Send raw message failed - ' + error_message)

    def __random_chain(self):

        # external ids must be in hex
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        content = binascii.hexlify(create_random_string(1024))

        return external_ids, content

    def __failure_data(self, commit_response):
        message = str(commit_response['message'])
        info = str(commit_response['data']['info'])
        entryhash = str(commit_response['data']['entryhash'])
        return message, info, entryhash
