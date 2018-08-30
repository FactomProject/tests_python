import unittest, time

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_debug import APIObjectsDebug
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_chain_in_block, wait_for_entry_in_block, fund_entry_credit_address
from helpers.api_methods import generate_random_external_ids_and_content

@attr(fast=True)
class APIEntriesTests(unittest.TestCase):
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    api_debug = APIObjectsDebug()
    cli_chain = CLIObjectsChain()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']

    def setUp(self):
        self.data = read_data_from_json('shared_test_data.json')
        self.entry_credit_address1000 = fund_entry_credit_address(1000)

    def test_compose_commit_reveal_entry(self):
        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000)

        # commit chain
        commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal_chain
        reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])

        chain_external_ids.insert(0, '-h')
        chain_external_ids.insert(2, '-h')

        status = wait_for_chain_in_block(external_id_list=chain_external_ids)

        # compose entry
        entry_external_ids, content = generate_random_external_ids_and_content()
        compose = self.api_wallet.compose_entry(reveal['chainid'], entry_external_ids, content, self.entry_credit_address1000)

        # commit entry
        commit = self.api_factomd.commit_entry(compose['commit']['params']['message'])
        # reveal entry
        reveal = self.api_factomd.reveal_entry(compose['reveal']['params']['entry'])

        # entry arrived in block?
        wait_for_entry_in_block(reveal['entryhash'], reveal['chainid'])
        self.assertIn('DBlockConfirmed',
                      str(self.api_factomd.get_status(reveal['entryhash'], reveal['chainid'])), 'Entry not arrived in block')

        # look for entry by hash
        self.assertIn(reveal['chainid'], str(self.api_factomd.get_entry_by_hash(reveal['entryhash'])), 'Entry with entryhash ' + reveal['entryhash'] + ' not found')

    def test_pending_entries(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)

        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address100)

        # commit chain
        self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal  = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])

        for x in range(0, self.blocktime+1):
            pending = self.api_factomd.get_pending_entries()
            # finished if non-empty
            if (pending and not str(pending).isspace()): break
            else: time.sleep(1)
        self.assertLess(x, self.blocktime, 'Entry ' + reveal['entryhash'] + ' never pending')
        self.assertIn(reveal['entryhash'], str(pending), 'Entry not pending')

    def test_receipt(self):
        self.entry_credit_address100 = fund_entry_credit_address(100)

        chain_external_ids, content = generate_random_external_ids_and_content()

        # compose chain
        compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address100)

        # commit chain
        self.api_factomd.commit_chain(compose['commit']['params']['message'])

        # reveal chain
        reveal  = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])

        chain_external_ids.insert(0, '-h')
        chain_external_ids.insert(2, '-h')

        wait_for_chain_in_block(external_id_list=chain_external_ids)
        receipt  = self.api_factomd.get_receipt(reveal['entryhash'])
        self.assertEquals(receipt['receipt']['entry']['entryhash'], receipt['receipt']['merklebranch'][0]['left'], 'Receipt entryhash ' + receipt['receipt']['merklebranch'][0]['left'] + ' does not match entryhash ' + receipt['receipt']['entry']['entryhash'])





