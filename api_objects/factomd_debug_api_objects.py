import requests
import json

from helpers.helpers import read_data_from_json


class FactomDebugApiObjects():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://'+self.factomd_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text, r.status_code

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
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
        return federated_servers

    def get_audit_servers(self):
        '''
        Get the list of the audit servers
        :return: the list of audit servers
        '''
        audit_servers = json.loads(self.send_get_request_with_method('audit-servers'))
        return audit_servers

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