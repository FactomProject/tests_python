import requests
import json
from helpers.helpers import read_data_from_json

class EnterpriseWalletObjects():
    data = read_data_from_json('addresses.json')
    enterprisewallet_address = data['enterprisewallet_address']
    url_get = 'http://'+ enterprisewallet_address + '/GET?request='
    url_post = 'http://'+ enterprisewallet_address + '/POST?request='
    status = True

    online = 'on'
    transactions = 'related-transactions'
    synced = 'synced'
    addresses = 'addresses'
    getaddress = 'get-address'
    addressnobal = 'addresses-no-bal'
    balances = 'balances'
    deladdress = 'delete-address'
    addressnamechange = 'address-name-change'
    displayprivatekey = 'display-private-key'
    newfctaddress ='generate-new-address-factoid'
    newecaddress ='generate-new-address-ec'
    importaddress = 'new-address'
    importkoinify = 'import-koinify'
    newexternaladdress = 'new-external-address'

    def send_post_request(self,request, payload):
        r = requests.post("http://localhost:8091/POST?request=" + request + "&json=" + payload)
        print "http://localhost:8091/POST?request=" + request + "&json=" + payload
        print r.text
        return r.text


    def send_get_request(self,request):
        r = requests.get(self.url_get + request)
        print r.text
        return r.text


    def get_status_enterprise_wallet(self):
        result = self.send_get_request(self.online)
        return result

    def get_transactions_from_enterprise(self):
        # http://localhost:8091/GET?request=related-transactions
        result = self.send_get_request(self.transactions)
        return result

    def get_synched_status(self):
        result = self.send_get_request(self.synced)
        return result

    def get_addresses(self):
        result = self.send_get_request(self.addresses)
        return result

    def get_address(self,address):
        payload = '{"Address":"' + address + '"}'
        result = self.send_post_request(self.getaddress,payload)
        return result

    def get_address_only(self):
        result = self.send_get_request(self.addressnobal)
        return result

    def get_balances(self):
        result = self.send_get_request(self.balances)
        return result

    def change_address_name(self,address,name):
        payload = '{"Address":"' + address + '","Name":"' + name + '"}'
        result = self.send_post_request(self.addressnamechange,payload)
        return result

    def delete_address(self,address):
        payload = '{"Address":"' + address + '"}'
        result = self.send_post_request(self.deladdress,payload)
        if result.find("Not a post valid request"):
            self.status = False
            result = "Failed"
        return result

    def display_private_key(self,address):
        payload = '{"Address":"' + address + '"}'
        result = self.send_post_request(self.displayprivatekey,payload)
        return result

    def generate_new_factoid_address(self,name):
        payload = name
        result = self.send_post_request(self.newfctaddress,payload)
        return result

    def generate_new_entrycredit_address(self,name):
        payload = name
        result = self.send_post_request(self.newecaddress,payload)
        return result

    def import_address_private_key(self,name,privatekey):
        payload = '{"Name":"' + name + '","Secret":"' + privatekey + '"}'
        result = self.send_post_request(self.importaddress,payload)
        return result

    def import_koinify_address(self,name,koinify):
        payload = '{"Name":"' + name + '","Koinify":"' + koinify + '"}'
        result = self.send_post_request(self.importkoinify,payload)
        return result

    def import_new_external_address(self,name,address):
        payload = '{"Name":"' + name + '","Public":"' + address + '"}'
        result = self.send_post_request(self.newexternaladdress,payload)
        return result