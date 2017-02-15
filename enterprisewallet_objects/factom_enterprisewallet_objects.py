import requests
import json
from helpers.helpers import read_data_from_json

class EnterpriseWalletObjects():
    data = read_data_from_json('addresses.json')
    enterprisewallet_address = data['enterprisewallet_address']
    url_get = 'http://'+ enterprisewallet_address + '/GET?request='
    url_post = 'http://'+ enterprisewallet_address + '/POST?request=get-address&json='

    transactions = 'related-transactions'
    synced = 'synced'
    addresses = 'addresses'

    def get_transactions_from_enterprise(self):
        # http://localhost:8091/GET?request=related-transactions
        input = self.transactions
        r = requests.get(self.url_get + input)
        return r.text

    def get_synched_status(self):
        input = self.synced
        r = requests.get(self.url_get + input)
        return r.text

    def get_addresses(self):
        input = self.addresses
        r = requests.get(self.url_get + input)
        return r.text

    def get_address(self,address):
        payload = '{"Address":"' + address + '"}'
        r = requests.post(self.url_post + payload)
        return r.text