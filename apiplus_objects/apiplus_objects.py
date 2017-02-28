import requests
import json

from helpers.helpers import read_data_from_json


class ApiplusApiObjects():

    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    apiplus_address = 'http://localhost:4000'
    chains = '/chains'
    entries = '/entries'
    first = '/first'
    last = '/last'


    def get_list_of_chains(self):
        r = requests.get(self.apiplus_address + self.chains)
        return json.loads(r.text)

    def get_chain_by_chainid(self, chain_id):
        r = requests.get(self.apiplus_address + self.chains + '/' + chain_id)
        return json.loads(r.text)

    def create_new_chain(self, chain_first_entry, *external_ids):
        ids = list(external_ids)
        payload = {'content': chain_first_entry, 'external_ids': ids}
        r = requests.post(self.apiplus_address + self.chains, json=payload)
        return json.loads(r.text)

    def list_chain_entries(self, chain_id):
        r = requests.get(self.apiplus_address + self.chains + '/' + chain_id + self.entries)
        return json.loads(r.text)

    def create_entry_in_chain(self, chain_id, content, *external_ids):
        ids = list(external_ids)
        payload = {'content': content, 'external_ids': ids}
        print payload
        r = requests.post(self.apiplus_address + self.chains + '/' + chain_id + self.entries, json=payload)
        return json.loads(r.text)

    def get_first_chain_entry(self, chain_id):
        r = requests.get(self.apiplus_address + self.chains + '/' + chain_id + self.entries + self.first)
        return json.loads(r.text)

    def get_last_chain_entry(self, chain_id):
        r = requests.get(self.apiplus_address + self.chains + '/' + chain_id + self.entries + self.last)
        return json.loads(r.text)

    def get_entry_by_chain_id_and_entry_id(self, chain_id, entry_id):
        r = requests.get(self.apiplus_address + self.chains + '/' + chain_id + self.entries + '/' + entry_id)
        return json.loads(r.text)