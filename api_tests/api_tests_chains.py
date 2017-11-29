import unittest
import os, binascii

from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_entry_in_block, fund_entry_credit_address
from nose.plugins.attrib import attr

@attr(api=True)
class APIChainsTests(unittest.TestCase):

    def setUp(self):
        self.api_objects_factomd = APIObjectsFactomd()
        self.api_objects_wallet = APIObjectsWallet()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_send_raw_message(self):
        # commit chain
        message, external_ids = self.__random_chain()
        print 'message', message
        self.api_objects_factomd.send_raw_message(message)

    def test_raw_create_chain(self):
        '''
        Create a new chain
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param content: str, the content (in hex) of the 1st entry of the chain
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
        :return txid: str
        :return entryhash: str
        :return chainid: str
        :return error_message: str, nil for no error
        '''
        txid = ''
        entryhash = ''
        chainid = ''
        external_ids, content = self.__random_chain()
        compose, error_message = self.compose_chain(external_ids, content, self.entry_credit_address1000)
        print 'compose', compose
        if not error_message:
            commit, error_message = self.commit_chain(compose['commit']['params']['message'])
            print 'commit', commit
            if not error_message:
                reveal, error_message = self.reveal_chain(compose['reveal']['params']['entry'])
                print 'reveal', reveal
                if not error_message:
                    txid = commit['txid']
                    entryhash = commit['entryhash']
                    chainid = reveal['chainid']
        return txid, entryhash, chainid, error_message

    def test_commit_chain(self):
        # commit chain
        external_ids, content = self.__random_chain()
        compose, error_message = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)
        print 'compose', compose
        if not error_message:
            commit, error_message = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            print 'commit', commit
            if error_message:
                fail_message, info, entryhash = self.__failure_data(commit)
                self.assertTrue(False, 'Chain commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)

    def test_repeated_commits(self):
        balance_before = self.api_objects_factomd.get_entry_credits_balance_by_ec_address(self.entry_credit_address1000)

        # commit chain
        external_ids, content = self.__random_chain()
        compose, error_message = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)
        print 'compose', compose
        if not error_message:
            commit, error_message = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])
            print 'commit', commit
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
                print 'commit', commit
                if not error_message:
                    self.assertFalse(True, 'Repeated commit allowed - entryhash ' + str(commit['entryhash']))
                else:
                    fail_message, info, entryhash = self.__failure_data(commit)
                    self.assertIn('Repeated Commit', fail_message, 'Chain commit failed because of - ' + fail_message + ' - ' + info + ' instead of Repeated Commit - entryhash ' + entryhash)

                # see if 2nd commit has been mistakenly paid for
                wait_for_entry_in_block(external_id_list=external_ids)
                balance_after = self.api_objects_factomd.get_entry_credits_balance_by_ec_address(self.entry_credit_address1000)
                self.assertEqual(balance_before, balance_after + 12, 'Balance before commit = ' + str(balance_before) + '. Balance after commit = ' + str(balance_after) + '. Balance after single commit SHOULD be = ' + str(balance_after + 12))

    def __random_chain(self):

        # external ids must be in hex
        name_1 = binascii.b2a_hex(os.urandom(2))
        name_2 = binascii.b2a_hex(os.urandom(2))
        external_ids = [name_1, name_2]

        # content must be in hex
        content = binascii.hexlify(create_random_string(1024))

        # compose chain
        # message, entry = self.api_objects_wallet.compose_chain(external_ids, content, self.entry_credit_address1000)

        return external_ids, content

    def __failure_data(self, commit_response):
        print 'commit_response'
        message = str(commit_response['message'])
        info = str(commit_response['data']['info'])
        entryhash = str(commit_response['data']['entryhash'])
        return message, info, entryhash
