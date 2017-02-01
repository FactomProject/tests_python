from api_objects.factomd_debug_api_objects import FactomDebugApiObjects
import unittest

class FactomDebugAPITests(unittest.TestCase):

    def setUp(self):
        self.factomd_debug_api = FactomDebugApiObjects()


    def test_get_holding_messages_in_queue(self):
        holding_queue_msgs = self.factomd_debug_api.get_holding_queue()
        print(holding_queue_msgs)

    def test_get_audit_servers(self):
        audit_servers =  self.factomd_debug_api.get_audit_servers()
        print audit_servers

    def test_get_network_info(self):
        network_info = self.factomd_debug_api.get_network_info()
        print network_info

    def test_get_predictive_fer(self):
        predictive_fer = self.factomd_debug_api.get_predictive_fer()