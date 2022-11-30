import unittest, re
import time

from nose.plugins.attrib import attr
from api_objects.api_objects_debug import APIObjectsDebug
from helpers.helpers import read_data_from_json
from helpers.cli_methods import get_data_dump_from_server
import logging

@attr(debug=True)
class FactomDebugAPItests(unittest.TestCase):
    api_debug = APIObjectsDebug()

    def setUp(self):
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_address']
        self.controlpanel = read_data_from_json('faulting.json')
        self.factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                       data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                       data['factomd_address_6']]

    def test_get_federated_servers(self):
        self.api_debug.change_factomd_address(self.factomd_address)
        federated_servers = self.api_debug.get_federated_servers()
        self.assertFalse(re.search('Method not found',str(federated_servers)), "get federated server method is not found")
        fed_list = []
        for fedservers in federated_servers:
            for server in fedservers.values():
                if re.search((r'.{64}$'),str(server)):
                    fed_list.append(server)
        return fed_list

    def test_get_audit_servers(self):
        audit_servers = self.api_debug.get_audit_servers()
        self.assertFalse(re.search('Method not found',str(audit_servers)), "get audit server method is not found")
        audit_list = []
        for auditservers in audit_servers:
            for server in auditservers.values():
                if re.search((r'.{64}$'), str(server)):
                    audit_list.append(server)
        return audit_list


    def test_get_holding_messages_in_queue(self):
        holding_queue_msgs = self.api_debug.get_holding_queue()
        self.assertFalse(re.search('Method not found',str(holding_queue_msgs)),"holding message api is not found")
        logging.getLogger('cli_command').info(holding_queue_msgs)
                
        
    def test_get_predictive_fer(self):
        predictive_fer = self.api_debug.get_predictive_fer()
        self.assertFalse(re.search('Method not found',str(predictive_fer)), "get predictive fer is not found")
        logging.getLogger('cli_command').info(predictive_fer)

    def test_audit_servers(self):
        self.parse_federated_audit_servers("Audit")


    def test_federated_servers(self):
        self.parse_federated_audit_servers("Fed")


    def parse_federated_audit_servers(self,authority):
        output = self.get_raw_data()
        found = True
        if authority == "Fed":
            result = self.find_between(str(output),'FederatedServersStart===','FederatedServersEnd')
            fed_audit_list = self.api_debug.get_federated_servers()
        else:
            result = self.find_between(str(output), 'AuditServersStart===', 'AuditServersEnd')
            result = result.replace("online","")
            fed_audit_list = self.api_debug.get_audit_servers()
        server_list = result.split("\\n")
        if len(fed_audit_list) > 0 and len(server_list) > 0:
            self.assertTrue(len(fed_audit_list) == int(server_list[0]),"servers is not matching")
            server_list.remove(server_list[0])
            server_list.remove(server_list[len(server_list)-1])
            for servers in server_list:
                found = False
                if servers.endswith("F"):
                    servers = servers.replace("F","")
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
        configuration = self.api_debug.get_configuration()
        logging.getLogger('cli_command').info(configuration)



    def test_currentminute(self):
        currentminute = self.api_debug.get_currentminute()
        result = "current minute is %d" % currentminute['Minute']
        logging.getLogger('cli_command').info(result)


    def test_current_minute_on_all_nodes(self):
      for factomd_address_custom in self.factomd_address_custom_list:
          self.api_debug.change_factomd_address(self.factomd_address)
          currentminute = self.api_debug.get_currentminute()
          self.api_debug.change_factomd_address(factomd_address_custom)
          currentminute_1 = self.api_debug.get_currentminute()
          if (currentminute == currentminute_1):
              result = "current minute on node - %s and node %s is %d" % (
              self.factomd_address, factomd_address_custom, currentminute['Minute'])
          else:
            result= "mismatch in node %s (%d) and %s (%d) " % (self.factomd_address, currentminute['Minute'], factomd_address_custom, currentminute_1['Minute'])
            #try again before giving up
            time.sleep(5)
            logging.getLogger('cli_command').info(result)
            currentminute = self.api_debug.get_currentminute()
            currentminute_1 = self.api_debug.get_currentminute()
            self.assertTrue(currentminute == currentminute_1,
                                "mismatch in node %s (%d) and %s (%d) " % (self.factomd_address,currentminute['Minute'], factomd_address_custom, currentminute_1['Minute']))

    def get_raw_data(self):
        result = get_data_dump_from_server(self.controlpanel['default_server_address'])
        return result

    def test_summary(self):
        result = self.api_debug.get_summary()
        logging.getLogger('cli_command').info(result)


    def test_set_delay(self):
        result = self.api_debug.set_delay('20')
        delay = result['Delay']
        result = self.api_debug.get_delay()
        self.assertEqual(result['Delay'],delay,"Testcase passed. Delay has been set")

    def test_set_droprate(self):
        result = self.api_debug.set_droprate('10')
        droprate = result['DropRate']
        result = self.api_debug.get_droprate()
        self.assertEqual(result['DropRate'],droprate,"Testcase passed. Drop Rate has been set")

    def test_reload_configuration(self):
        result = self.api_debug.reload_configuration()
        logging.getLogger('cli_command').info(result)

    def test_process_list(self):
        result = self.api_debug.get_process_list()
        logging.getLogger('cli_command').info(result)

    def test_messages(self):
        result = self.api_debug.get_messages_list()
        logging.getLogger('cli_command').info(result)