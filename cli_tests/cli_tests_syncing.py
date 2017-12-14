import unittest
import time
import os

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers.helpers import read_data_from_json
from helpers.cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class CLITestsSyncing(unittest.TestCase):

    blocktime = int(os.environ['BLOCKTIME'])
    data_shared = read_data_from_json('shared_test_data.json')
    data_fault = read_data_from_json('faulting.json')
    data_sync = read_data_from_json('syncing.json')
    _faulting_command = 'docker stop factom-factomd-'
    _restart_command = 'docker start factom-factomd-'

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.chain_objects = CLIObjectsChain()

    def test_sync_stopped_node(self):

        # stop node
        send_command_to_cli_and_receive_text(self._faulting_command + self.data_fault['audit1'])
        time.sleep(self.blocktime)
        self.assertIn(self.data_fault['audit1_hash'] + ' offline', get_data_dump_from_server(self.data_fault['default_server_address']), 'Audit server ' + self.data_fault['audit1_hash'] + ' not faulted')

        # keep node stopped for a bit
        for i in xrange(self.data_sync['BLOCKS_TO_FALL_BEHIND']): time.sleep(self.blocktime)

        # restart node
        send_command_to_cli_and_receive_text(self._restart_command + self.data_fault['audit1'])

        while "connection refused" in self.chain_objects.get_heights(): pass

        # wait for node to resync
        synced = False
        start_time = time.time()
        while (time.time() - start_time < self.data_sync['SECONDS_TO_WAIT_FOR_SYNC']):
            heights = self.chain_objects.get_heights()
            directory_block_height = self.chain_objects.parse_transaction_data(heights)['DirectoryBlockHeight']
            leader_block_height = self.chain_objects.parse_transaction_data(heights)['LeaderHeight']
            if (directory_block_height == leader_block_height):
                synced = True
                break
        self.assertTrue(synced, 'Node did not sync up within ' + str(self.data_sync['SECONDS_TO_WAIT_FOR_SYNC']) + ' seconds')