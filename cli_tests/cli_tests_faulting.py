import unittest
import time

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import read_data_from_json
from helpers.cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class CLITestsFaulting(unittest.TestCase):
    data = read_data_from_json('faulting.json')
    _faulting_command = 'docker stop factom-factomd-'
    _restart_command = 'docker start factom-factomd-'

    def setUp(self):
        self.cli_create = CLIObjectsCreate()

    def test_fault_audit_server(self):
        '''
        Test that checking if you audit server is faulted and if network is not stalled after
        :return:
        '''
        self.assertIn(
            self.data['audit_1_hash'] + ' online', get_data_dump_from_server(self.data['default_server_address']), 'Audit server ' + self.data['audit_1_hash'] + ' is not online so can\'t be faulted')
        send_command_to_cli_and_receive_text(self._faulting_command + self.data['audit'])
        time.sleep(self.data['BLOCK_TIME'])
        self.assertIn(self.data['audit_1_hash'] + ' offline', get_data_dump_from_server(self.data['default_server_address']), 'Audit server ' + self.data['audit_1_hash'] + ' not faulted')
        send_command_to_cli_and_receive_text(self._restart_command + self.data['audit'])

    def test_fault_federated_server(self):
        '''
        Test that checking if federated server is faulted and if network is not stalled after
        :return:
        '''
        # self.assertIn(
        #     self.data['audit_2_hash'] + ' online', get_data_dump_from_server(self.data['default_server_address']), 'Audit server ' + self.data['audit_2_hash'] + ' is not online so can\'t be promoted')

        # make sure audit 1 is online
        # self.assertLess(self.wait_for_server_status_change('audit_1_hash', 'online'), 10, 'Audit server ' + self.data['audit_1_hash'] + ' is not online so can\'t be faulted')

        # take audit 1 offline so that audit 2 will be promoted when federated server is removed
        send_command_to_cli_and_receive_text(self._faulting_command + self.data['audit'])
        self.assertLess(self.wait_for_server_status_change('audit_1_hash', 'offline'), 10, 'Failed to take Audit server 1 ' + self.data['audit_1_hash'] + ' offline')

        # take federated server offline - create fault
        send_command_to_cli_and_receive_text(self._faulting_command + self.data['federated'])
        self.assertLess(self.wait_for_server_status_change('federated_hash', 'offline'), 10, 'Failed to take Federated server ' + self.data['federated_hash'] + ' offline')

        # check that audit 2 was promoted to federated server in place of removed node
        self.assertLess(self.wait_for_server_status_change('audit_2_hash', 'offline'), 10, 'Failed to take Audit server 1 ' + self.data['audit_1_hash'] + ' offline')

        send_command_to_cli_and_receive_text(self._restart_command + self.data['audit'])
        send_command_to_cli_and_receive_text(self._restart_command + self.data['federated'])

    def _wait_for_server_status_change(self, server_hash, status):
        x = 1
        while (server_hash + ' ' + status not in get_data_dump_from_server(self.data['default_server_address']) and x < 11):
            print 'waited ', x, ' blocks'
            x = x + 1
            time.sleep(self.data['BLOCK_TIME'])
        return x




            # self.assertTrue(
        #     self.data['audit_1_hash'] + ' offline' in get_data_dump_from_server(self.data['default_server_address']), 'Other audit server ' + self.data['audit_1_hash'] + ' not faulted')
