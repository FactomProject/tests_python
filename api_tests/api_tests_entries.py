import unittest

from nose.plugins.attrib import attr
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address
from helpers.api_methods import generate_random_external_ids_and_content
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet

from cli_objects.cli_objects_chain import CLIObjectsChain


@attr(api=True)
class APIEntriesTests(unittest.TestCase):

    def setUp(self):

        self.cli_chain = CLIObjectsChain()


        self.api_objects_factomd = APIObjectsFactomd()
        self.api_objects_wallet = APIObjectsWallet()
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    @unittest.expectedFailure
    def test_compose_commit_reveal_entry(self):
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose = self.api_objects_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)[0]

        # commit chain
        commit  = self.api_objects_factomd.commit_chain(compose['commit']['params']['message'])[0]

        # reveal_chain
        reveal  = self.api_objects_factomd.reveal_chain(compose['reveal']['params']['entry'])[0]

        # compose entry
        entry_external_ids, content = generate_random_external_ids_and_content()
        compose, compose_error = self.api_objects_wallet.compose_entry(reveal['chainid'], entry_external_ids, content, self.entry_credit_address1000)
        self.assertFalse(compose_error, 'Compose entry failed because ' + compose_error)

        # commit entry
        commit, commit_error  = self.api_objects_factomd.commit_entry(compose['commit']['params']['message'])
        if commit_error:
            fail_message, info, entryhash = self.commit_failure_data(commit)
            self.assertTrue(False, 'Entry commit failed - ' + fail_message + ' - ' + info + ' - entryhash ' + entryhash)

        else:
            # reveal entry
            reveal, reveal_error  = self.api_objects_factomd.reveal_entry(compose['reveal']['params']['entry'])
            if reveal_error:
                fail_message = str(reveal['message'])
                data = str(reveal['data'])
                self.assertTrue(False, 'Entry reveal failed - ' + fail_message + ' - ' + data)
            else:
                # search for revealed entry
                chain_external_ids.insert(0, '-h')
                chain_external_ids.insert(2, '-h')
                status = wait_for_chain_in_block(external_id_list=entry_external_ids)
                # status = wait_for_chain_in_block(external_id_list=chain_names_list)

                # entry arrived in block?
                self.assertIn('DBlockConfirmed', str(self.api_objects_factomd.get_status(reveal['entryhash'], reveal['chainid'])), 'Entry not arrived in block')

                # look for entry by hash
                self.assertIn(reveal['chainid'], str(self.api_objects_factomd.get_entry_by_hash(reveal['entryhash'])), 'Entry with entryhash ' + reveal['entryhash'] + ' not found')

    def test_pending_entries(self):
        # TODO replace following CLI 'make chain' code below with API 'compose chain' code once it is working
        self.entry_credit_address100 = fund_entry_credit_address(100)
        data = create_random_string(1024)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        names_list = ['-n', name_1, '-n', name_2]
        chain_flag_list = ['-E']
        entry_hash = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list, flag_list=chain_flag_list)

        self.assertIn(entry_hash, str(self.api_objects_factomd.get_pending_entries()), 'Entry not pending')



