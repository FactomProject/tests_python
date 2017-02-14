from api_objects.factomd_debug_api_objects import FactomDebugApiObjects
import unittest
import re
from helpers.helpers import read_data_from_json
import time
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server

class FactomDebugAPITests(unittest.TestCase):

    def setUp(self):
        self.factomd_debug_api = FactomDebugApiObjects()
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_address']
        self.factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                       data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                       data['factomd_address_6']]
        self.controlpanel = read_data_from_json('faulting.json')

    def test_get_holding_messages_in_queue(self):
        holding_queue_msgs = self.factomd_debug_api.get_holding_queue()
        self.assertFalse(re.search('Method not found',str(holding_queue_msgs)),"holding message api is not found")
        print(holding_queue_msgs)

    def get_federated_servers(self):
        self.factomd_debug_api.change_factomd_address(self.factomd_address)
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
        audit_list = []
        for auditservers in audit_servers:
            for server in auditservers.values():
                if re.search((r'.{64}$'), str(server)):
                    audit_list.append(server)
        return audit_list

    def test_get_network_info(self):
        network_info = self.factomd_debug_api.get_network_info()
        self.assertFalse(re.search('Method not found',str(network_info)), "get network info is not found")
        print network_info

    def test_get_predictive_fer(self):
        predictive_fer = self.factomd_debug_api.get_predictive_fer()
        self.assertFalse(re.search('Method not found',str(predictive_fer)), "get predictive fer is not found")
        print predictive_fer

    def test_audit_servers(self):
        self.parse_federated_audit_servers("Audit")


    def test_federated_servers(self):
        self.parse_federated_audit_servers("Fed")


    def parse_federated_audit_servers(self,authority):
        output = self.get_raw_data()
        found = True
        if authority == "Fed":
            result = self.find_between(str(output),'FederatedServersStart===','FederatedServersEnd')
            print result
            fed_audit_list = self.get_federated_servers()
            print fed_audit_list
        else:
            result = self.find_between(str(output), 'AuditServersStart===', 'AuditServersEnd')
            result = result.replace("online","")
            fed_audit_list = self.get_audit_servers()
        server_list = result.split("\\n")
        self.assertTrue(len(fed_audit_list) == int(server_list[0]),"servers is not matching")
        server_list.remove(server_list[0])
        server_list.remove(server_list[len(server_list)-1])
        for servers in server_list:
            found = False
            if servers.endswith("F"):
                servers = servers.replace("F","")
                print servers
            for fed_audit in fed_audit_list:
                if re.search(servers,str(fed_audit)):
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

    def test_get_configuration(self):
        configuration = self.factomd_debug_api.get_configuration()
        print configuration


    def test_droprate(self):
        droprate = self.factomd_debug_api.get_droprate()
        print droprate


    def test_currentminute(self):
        currentminute = self.factomd_debug_api.get_currentminute()
        print "current minute is %d" % currentminute


    def test_current_minute_on_all_nodes(self):
      for factomd_address_custom in self.factomd_address_custom_list:
          self.factomd_debug_api.change_factomd_address(self.factomd_address)
          currentminute = self.factomd_debug_api.get_currentminute()
          self.factomd_debug_api.change_factomd_address(factomd_address_custom)
          currentminute_1 = self.factomd_debug_api.get_currentminute()
          if (currentminute == currentminute_1):
              print "current minute on node - %s and node %s is %d" % (
              self.factomd_address, factomd_address_custom, currentminute)
          else:
            print "mismatch in node %s (%d) and %s (%d) " % (self.factomd_address, currentminute, factomd_address_custom, currentminute_1)
            #try again before giving up
            time.sleep(5)
            currentminute = self.factomd_debug_api.get_currentminute()
            currentminute_1 = self.factomd_debug_api.get_currentminute()
            self.assertTrue(currentminute == currentminute_1,
                                "mismatch in node %s and %s" % (self.factomd_address, factomd_address_custom))

    def get_raw_data(self):
        result = get_data_dump_from_server(self.controlpanel['default_server_address'])
        return result