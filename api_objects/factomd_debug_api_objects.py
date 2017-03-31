import requests
import json

from helpers.helpers import read_data_from_json


class FactomDebugApiObjects():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def change_factomd_address(self, value):
         self.factomd_address = value

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://'+self.factomd_address+'/debug'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text, r.status_code

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/debug'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.url
        print r.text
        return r.text

    def get_holding_queue(self):
        '''
        Show holding messages in the queue
        :return: holding messages in the queue
        '''
        holding_queue = json.loads(self.send_get_request_with_method('holding-queue'))
        return holding_queue

    def get_federated_servers(self):
        '''
        Get the list of the federated servers
        :return: the list of federated servers
        '''
        federated_servers = json.loads(self.send_get_request_with_method('federated-servers'))
        return federated_servers["result"]["FederatedServers"]

    def get_audit_servers(self):
        '''
        Get the list of the audit servers
        :return: the list of audit servers
        '''
        audit_servers = json.loads(self.send_get_request_with_method('audit-servers'))
        return audit_servers["result"]["AuditServers"]

    def get_network_info(self):
        '''
        Get the network information
        :return: the network information
        '''
        network_info = json.loads(self.send_get_request_with_method('network-info'))
        return network_info

    def get_predictive_fer(self):
        '''
        Get the predicted future exchange rate
        :return: Get the predicted future exchange rate
        '''
        predictive_fer = json.loads(self.send_get_request_with_method('predictive-fer'))
        return predictive_fer

    def get_configuration(self):
        '''
        Get the configuration from the config file
        :return: Get the configuration from the config file
        '''
        configuration = json.loads(self.send_get_request_with_method('configuration'))
        return configuration

    def get_droprate(self):
        '''
        Get the drop rate of factomd
        :return: Get the drop rate of factomd
        '''
        droprate = json.loads(self.send_get_request_with_method('drop-rate'))
        return droprate

    def set_droprate(self,droprate):
        '''
        Set the drop rate of factomd node
        :return: Set the drop rate of factomd node
        '''
        delay = json.loads(self.send_get_request_with_params_dict('droprate', {'droprate': droprate})[0])
        return delay

    def get_currentminute(self):
        '''
        Get the current minute of factomd
        :return: Get the current minute of factomd
        '''
        currentminute = json.loads(self.send_get_request_with_method('current-minute'))
        return currentminute["result"]

    def get_summary(self):
        '''
        Get the summary of factomd
        :return: Get the summary of factomd
        '''
        summary = json.loads(self.send_get_request_with_method('summary'))
        return summary

    def get_delay(self):
        '''
        Get the delay of factomd node
        :return: Get the delay of factomd
        '''
        delay = json.loads(self.send_get_request_with_method('delay'))
        return delay

    def set_delay(self,delay):
        '''
        Set the delay of factomd node
        :return: Set the delay of factomd node
        '''
        delay = json.loads(self.send_get_request_with_params_dict('delay', {'delay': delay})[0])
        return delay

    def reload_configuration(self):
        conf = json.loads(self.send_get_request_with_method('reload-configuration'))
        return conf

    def get_process_list(self):
        processlist =  json.loads(self.send_get_request_with_method('process-list'))
        return processlist

    def get_messages_list(self):
        messages = json.loads(self.send_get_request_with_method('messages'))
        return messages