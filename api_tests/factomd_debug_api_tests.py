from api_objects.factomd_debug_api_objects import FactomDebugApiObjects
import unittest
import re

class FactomDebugAPITests(unittest.TestCase):

    def setUp(self):
        self.factomd_debug_api = FactomDebugApiObjects()


    def get_holding_messages_in_queue(self):
        holding_queue_msgs = self.factomd_debug_api.get_holding_queue()
        self.assertFalse(re.search('Method not found',str(holding_queue_msgs)),"holding message api is not found")
        print(holding_queue_msgs)

    def get_federated_servers(self):
        federated_servers = self.factomd_debug_api.get_federated_servers()
        self.assertFalse(re.search('Method not found',str(federated_servers)), "get federated server is not found")
        fed_list = []
        for fedservers in federated_servers:
            for server in fedservers.values():
                if re.search((r'.{64}$'),str(server)):
                    fed_list.append(server)
        return fed_list

    def get_audit_servers(self):
        audit_servers = self.factomd_debug_api.get_audit_servers()
        self.assertFalse(re.search('Method not found',str(audit_servers)), "get audit server is not found")
        print audit_servers

    def get_network_info(self):
        network_info = self.factomd_debug_api.get_network_info()
        self.assertFalse(re.search('Method not found',str(network_info)), "get network info is not found")
        print network_info

    def get_predictive_fer(self):
        predictive_fer = self.factomd_debug_api.get_predictive_fer()
        self.assertFalse(re.search('Method not found',str(predictive_fer)), "get predictive fer is not found")
        print predictive_fer

    def test_parse_federated_audit_servers(self):
        with open('/home/veena/Factom/tests_python/datadump.txt', 'rt') as in_file:
            output = in_file.read()
            found = True
            result = self.find_between(str(output),'FederatedServersStart===','FederatedServersEnd')
            server_list = result.split("\\n")
            fed_list = self.get_federated_servers()
            self.assertTrue(len(fed_list) == int(server_list[0]),"number of federated servers is not matching")
            server_list.remove(server_list[0])
            server_list.remove(server_list[len(server_list)-1])
            for servers in server_list:
                found = False
                for chains in fed_list:
                    if re.search(servers,str(chains)):
                        found = True
                        break
            self.assertTrue(found, "federated server identity is not matching")

    def find_between(self, s, first, last):
        try:
            start = s.rindex( first ) + len( first )
            end = s.index( last, start )
            return (s[start:end]).replace(" ","")
        except ValueError:
            return ""
