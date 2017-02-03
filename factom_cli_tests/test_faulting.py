import unittest
import time

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from helpers.helpers import read_data_from_json
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class FactomTestFaulting(unittest.TestCase):
    data = read_data_from_json('faulting.json')
    _faulting_command = 'docker stop factom-factomd-'

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()


    def test_fault_audit_server(self):
        '''
        Test that checking if you audit server is faulted and if network is not stalled after
        :return:
        '''
        self.assertTrue(
            '888888271203752870ae online' in get_data_dump_from_server(self.data['default_server_address']))

        time.sleep(self.data['time_to_wait'])
        self.assertTrue('888888271203752870ae offline' in get_data_dump_from_server(self.data['default_server_address']))

    def test_fault_federated_server(self):
        '''
        Test that checking if federated server is faulted and if network is not stalled after
        :return:
        '''
        self.assertTrue(
            ' 888888a21d5ac004defa online' in get_data_dump_from_server(
                self.data['default_server_address']))
        send_command_to_cli_and_receive_text(self._faulting_command + self.data['federated'])
        time.sleep(self.data['time_to_wait'])
        self.assertTrue(
            '888888271203752870ae offline' and ' 888888e238492b2d723d offline' in get_data_dump_from_server(self.data['default_server_address']))






