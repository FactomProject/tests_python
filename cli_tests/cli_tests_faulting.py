import unittest, time, json

from nose.plugins.attrib import attr

from cli_objects.cli_objects_create import CLIObjectsCreate
from api_objects.api_objects_debug import APIObjectsDebug
from helpers.helpers import read_data_from_json
from helpers.cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

@attr(slow=True)
class CLITestsFaulting(unittest.TestCase):
    data = read_data_from_json('faulting.json')
    _stop_command = 'sudo docker stop factom-factomd-'
    _restart_command = 'sudo docker start factom-factomd-'

    # NOTE if these tests are interrupted before they finish, the network server configuration may be altered

    def setUp(self):
        self.cli_create = CLIObjectsCreate()
        self.api_debug = APIObjectsDebug()

    def test_fault_audit_server(self):

        # take audit server offline - create fault
        send_command_to_cli_and_receive_text(self._stop_command + self.data['audit1'])
        self.assertLess(self.wait_for_server_status_change('audit', self.data['audit1_full'], 'offline'), self.data['BLOCKS_TO_WAIT'], 'Failed to take Audit server ' + self.data['audit1_full'] + ' offline')

        # restart faulted audit server
        send_command_to_cli_and_receive_text(self._restart_command + self.data['audit1'])
        self.assertLess(self.wait_for_server_status_change('audit', self.data['audit1_full'], 'online'), self.data['BLOCKS_TO_WAIT'], 'Failed to restart Audit server ' + self.data['audit1_full'])

    def test_fault_federated_server(self):

        # This test will only work reliably if there are exactly 2 audit servers

        # take audit2 offline so that audit1 will be promoted when federated server is removed
        send_command_to_cli_and_receive_text(self._stop_command + self.data['audit2'])
        self.assertLess(self.wait_for_server_status_change('audit', self.data['audit2_full'], 'offline'), self.data['BLOCKS_TO_WAIT'], 'Failed to take Audit server 2 ' + self.data['audit2_full'] + ' offline')

        # take federated server offline - create fault
        send_command_to_cli_and_receive_text(self._stop_command + self.data['federated'])
        self.assertLess(self.wait_for_server_status_change('federated', self.data['federated_full'], 'offline'), self.data['BLOCKS_TO_WAIT'], 'Failed to take Federated server ' + self.data['federated_full'] + ' offline')

        # check that audit1 was promoted to federated server in place of removed node
        self.assertLess(self.wait_for_server_status_change('federated', self.data['audit1_full'], 'online'),
                        self.data['BLOCKS_TO_WAIT'], 'Audit server 1 ' + self.data['audit1_full'] + ' did not replace faulted federated server ' + self.data['federated_full'])

        # restart faulted servers

        # restart faulted audit server
        send_command_to_cli_and_receive_text(self._restart_command + self.data['audit2'])
        self.assertLess(self.wait_for_server_status_change('audit', self.data['audit2_full'], 'online'), self.data['BLOCKS_TO_WAIT'], 'Failed to restart Audit server 2 ' + self.data['audit2_full'])

        # restart faulted federated server
        send_command_to_cli_and_receive_text(self._restart_command + self.data['federated'])
        self.assertLess(self.wait_for_server_status_change('audit', self.data['federated_full'], 'online'), self.data['BLOCKS_TO_WAIT'], 'Failed to restart Federated server ' + self.data['federated_full'])

        # restore original configuration

        # promote audit1 from federated server back to audit server
        send_command_to_cli_and_receive_text('addservermessage -host=' + self.data['default_server_port'] + ' send a ' + self.data['audit1_full'] + ' ' + self.data['default_private_key'])

        # promote federated from audit server back to federated server
        send_command_to_cli_and_receive_text('addservermessage -host=' + self.data['default_server_port'] + ' send f ' + self.data['federated_full'] + ' ' + self.data['default_private_key'])

    def wait_for_server_status_change(self, server_type, server_hash, status):
        '''
        The online/offline status of the server of type server_type ('federated' or 'audit') identified by the identity server_hash (888888...) will be monitored until either its status matches the requested input status ('online' or something else) or the number of blocks elapsed exceeds a preset limit (BLOCKS_TO_WAIT).
        :param server_type: 'federated' or 'audit'; used to get a list of either all the current federated servers or all the current audit servers along with their online or offline status via the calls api_objects_debug/get_federated_servers() or api_objects_debug/get_audit_servers(). The call is constructed using the parameter, so if the parameter is incorrectly specified, the call will fail.
        :return blocks_waited; This is the number of blocks elapsed before the sought situation was found. If this equals the BLOCKS_TO_WAIT limit on the number of blocks to search, then the search failed.
        '''
        command = 'result = self.api_debug.get_' + server_type + '_servers()'

        """
        :param server_hash: the full hash of the identity of the server whose status is being queried
        :param status: 'online' or something else; the desired status of the server. Processing will continue until either this status is achieved or BLOCKS_TO_WAIT number of blocks have elapsed.
        :return: list of dicts with entries
        """
        if status == 'online':
            online = 'True'
        else:
            online = 'False'

        blocks_waited = 0
        while (blocks_waited < (self.data['BLOCKS_TO_WAIT'] + 1)):
            exec(command)
            for server, data in enumerate(result):
                data_string = str(data)
                found = server_hash in data_string
                if found: break
            blocks_waited += 1
            if (found and 'Online\': ' + online in data_string): break
            time.sleep(self.data['BLOCK_TIME'])
        self.assertTrue(found, 'Server ' + server_hash + ' is not ' + server_type + ' server')
        return blocks_waited