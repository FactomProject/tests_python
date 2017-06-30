import unittest
import time

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class FactomTestFaulting(unittest.TestCase):
    data_shared = read_data_from_json('shared_test_data.json')
    data_fault = read_data_from_json('faulting.json')
    _faulting_command = 'docker stop factom-factomd-'
    _restart_command = 'docker start factom-factomd-'
    BLOCKS_TO_FALL_BEHIND = 2
    SECONDS_TO_WAIT_FOR_SYNC = 6000

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()


    def test_sync_stopped_node(self):

        # stop node
        send_command_to_cli_and_receive_text(self._faulting_command + self.data_fault['audit'])
        time.sleep(self.data_shared['BLOCKTIME'])
        self.assertIn(self.data_fault['audit_1_hash'] + ' offline', get_data_dump_from_server(self.data_fault['default_server_address']), 'Audit server ' + self.data_fault['audit_1_hash'] + ' not faulted')

        # keep node stopped for a bit
        for i in xrange(self.BLOCKS_TO_FALL_BEHIND): time.sleep(self.data_shared['BLOCKTIME'])

        # restart node
        send_command_to_cli_and_receive_text(self._restart_command + self.data_fault['audit'])

        while "connection refused" in self.factom_chain_object.get_heights(): pass

        # wait for node to resync
        synced = False
        start_time = time.time()
        while (time.time() - start_time < self.SECONDS_TO_WAIT_FOR_SYNC):
            heights = self.factom_chain_object.get_heights()
            directory_block_height = self.factom_chain_object.parse_transaction_data(heights)['DirectoryBlockHeight']
            leader_block_height = self.factom_chain_object.parse_transaction_data(heights)['LeaderHeight']
            if (directory_block_height == leader_block_height):
                synced = True
                break
        self.assertTrue(synced, 'Node did not sync up within ' + str(self.SECONDS_TO_WAIT_FOR_SYNC) + ' seconds')