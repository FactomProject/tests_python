import unittest
import time

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import read_data_from_json
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class CLITestsFaulting(unittest.TestCase):
    data = read_data_from_json('faulting.json')
    _faulting_command = 'docker stop factom-factomd-'

    def setUp(self):
        self.factom_cli_create = CLIObjectsCreate()


    def _fault_audit_server(self):
        '''
        Test that checking if you audit server is faulted and if network is not stalled after
        :return:
        '''
        self.assertTrue(
            self.data['audit_1_hash'] + ' online' in get_data_dump_from_server(self.data['default_server_address']))
        send_command_to_cli_and_receive_text(self._faulting_command + self.data['audit'])
        time.sleep(self.data['time_to_wait'])
        self.assertTrue(self.data['audit_1_hash'] + ' offline' in get_data_dump_from_server(self.data['default_server_address']))

    def test_fault_federated_server(self):
        '''
        Test that checking if federated server is faulted and if network is not stalled after
        :return:
        '''
        self.assertTrue(
            self.data['audit_2_hash'] + ' online' in get_data_dump_from_server(
                self.data['default_server_address']))
        send_command_to_cli_and_receive_text(self._faulting_command + self.data['federated'])
        time.sleep(self.data['time_to_wait'])
        self.assertTrue(
            self.data['audit_1_hash'] + ' offline' and  self.data['master_hash'] + ' offline' in get_data_dump_from_server(self.data['default_server_address']))
