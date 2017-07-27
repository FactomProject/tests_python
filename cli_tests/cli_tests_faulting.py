import unittest
import time

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from api_objects.api_objects_debug import ApiObjectsDebug
from helpers.helpers import read_data_from_json
from helpers.cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class CLITestsFaulting(unittest.TestCase):
    data = read_data_from_json('faulting.json')
    _stop_command = 'docker stop factom-factomd-'
    _restart_command = 'docker start factom-factomd-'

    # NOTE if these tests are interrupted before they finish, the network server configuration may be altered

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.api_debug = ApiObjectsDebug()

    def test_fault_audit_server(self):

        # take audit server offline - create fault
        send_command_to_cli_and_receive_text(self._stop_command + self.data['audit1'])
        self.assertLess(self._wait_for_server_status_change(self.data['audit1_hash'], 'offline'), self.data['BLOCKS_TO_WAIT'], 'Failed to take Audit server ' + self.data['audit1_hash'] + ' offline')

        # restart faulted audit server
        send_command_to_cli_and_receive_text(self._restart_command + self.data['audit1'])
        self.assertLess(self._wait_for_server_status_change(self.data['audit1_hash'], 'online'), self.data['BLOCKS_TO_WAIT'], 'Failed to restart Audit server ' + self.data['audit1_hash'])

    def test_fault_federated_server(self):

        # This test will only work reliably if there are exactly 2 audit servers

        # take audit2 offline so that audit1 will be promoted when federated server is removed
        send_command_to_cli_and_receive_text(self._stop_command + self.data['audit2'])
        self.assertLess(self._wait_for_server_status_change(self.data['audit2_hash'], 'offline'), self.data['BLOCKS_TO_WAIT'], 'Failed to take Audit server 2 ' + self.data['audit2_hash'] + ' offline')

        # take federated server offline - create fault
        send_command_to_cli_and_receive_text(self._stop_command + self.data['federated'])
        self.assertLess(self._wait_for_server_status_change(self.data['federated_hash'], 'offline'), self.data['BLOCKS_TO_WAIT'], 'Failed to take Federated server ' + self.data['federated_hash'] + ' offline')

        # check that audit1 was promoted to federated server in place of removed node
        blocks_waited = 0
        while (self.data['audit1_hash'] not in str(self.api_debug.get_federated_servers()) and blocks_waited < (self.BLOCKS_TO_WAIT+1)):
            blocks_waited += 1
            time.sleep(self.data['BLOCK_TIME'])
        self.assertLess(blocks_waited, self.data['BLOCKS_TO_WAIT'], 'Audit server 1 ' + self.data['audit1_hash'] + ' did not replace faulted federated server ' + self.data['federated_hash'])

        # restart faulted servers

        # restart faulted audit server
        send_command_to_cli_and_receive_text(self._restart_command + self.data['audit2'])
        self.assertLess(self._wait_for_server_status_change(self.data['audit2_hash'], 'online'), self.data['BLOCKS_TO_WAIT'], 'Failed to restart Audit server 2 ' + self.data['audit2_hash'])

        # restart faulted federated server
        send_command_to_cli_and_receive_text(self._restart_command + self.data['federated'])
        self.assertLess(self._wait_for_server_status_change(self.data['federated_hash'], 'online'), self.data['BLOCKS_TO_WAIT'], 'Failed to restart Federated server ' + self.data['federated_hash'])

        # restore original configuration

        # promote audit1 from federated server back to audit server
        send_command_to_cli_and_receive_text('addservermessage -host=' + self.data['default_server_port'] + ' send a ' + self.data['audit1_full'] + ' ' + self.data['default_private_key'])

        # promote federated from audit server back to federated server
        send_command_to_cli_and_receive_text('addservermessage -host=' + self.data['default_server_port'] + ' send f ' + self.data['federated_full'] + ' ' + self.data['default_private_key'])

    def _wait_for_server_status_change(self, server_hash, status):
        blocks_waited = 0
        while (server_hash + ' ' + status not in str(get_data_dump_from_server(self.data['default_server_address'])) and blocks_waited < (self.data['BLOCKS_TO_WAIT']+1)):
            blocks_waited += 1
            time.sleep(self.data['BLOCK_TIME'])
        return blocks_waited
