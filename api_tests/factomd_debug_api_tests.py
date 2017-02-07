from api_objects.factomd_debug_api_objects import FactomDebugApiObjects
import unittest
import re

class FactomDebugAPITests(unittest.TestCase):

    def setUp(self):
        self.factomd_debug_api = FactomDebugApiObjects()


    def test_get_holding_messages_in_queue(self):
        holding_queue_msgs = self.factomd_debug_api.get_holding_queue()
        self.assertFalse(re.search('Method not found',str(holding_queue_msgs)),"holding message api is not found")
        print(holding_queue_msgs)

    def test_get_federated_servers(self):
        federated_servers = self.factomd_debug_api.get_federated_servers()
        self.assertFalse(re.search('Method not found',str(federated_servers)), "get federated server is not found")
        print federated_servers

    def test_get_audit_servers(self):
        audit_servers = self.factomd_debug_api.get_audit_servers()
        self.assertFalse(re.search('Method not found',str(audit_servers)), "get audit server is not found")

        print audit_servers

    def test_get_network_info(self):
        network_info = self.factomd_debug_api.get_network_info()
        self.assertFalse(re.search('Method not found',str(network_info)), "get network info is not found")
        print network_info

    def test_get_predictive_fer(self):
        predictive_fer = self.factomd_debug_api.get_predictive_fer()
        self.assertFalse(re.search('Method not found',str(predictive_fer)), "get predictive fer is not found")
        print predictive_fer

    def test_parse_federated_audit_servers(self):
        with open('/home/factom/Factom/tests_python/datadump.txt', 'rt') as in_file:
            output = in_file.read()
            print output


