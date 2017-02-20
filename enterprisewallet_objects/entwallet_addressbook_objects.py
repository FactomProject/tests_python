
from helpers.helpers import read_data_from_json
from enterprisewallet_objects.entwallet_objects import EnterpriseWalletObjects

class EnterpriseWalletAddressBookObjects():

    def __init__(self):
        self.enterprisewallet = EnterpriseWalletObjects()
        self.data = read_data_from_json('addresses.json')
        self.addresses = 'addresses'
        self.getaddress = 'get-address'
        self.addressnobal = 'addresses-no-bal'
        self.balances = 'balances'
        self.deladdress = 'delete-address'
        self.addressnamechange = 'address-name-change'
        self.displayprivatekey = 'display-private-key'
        self.newfctaddress ='generate-new-address-factoid'
        self.newecaddress ='generate-new-address-ec'
        self.importaddress = 'new-address'
        self.importkoinify = 'import-koinify'
        self.newexternaladdress = 'new-external-address'

    def get_addresses(self):
        result = self.enterprisewallet.send_get_request(self.addresses)
        return result

    def get_address(self,address):
        payload =(('request', self.getaddress), (
        'json',  '{"Address":"' + address + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def get_address_only(self):
        result = self.enterprisewallet.send_get_request(self.addressnobal)
        return result

    def get_balances(self):
        result = self.enterprisewallet.send_get_request(self.balances)
        return result

    def change_address_name(self,address,name):
        payload = (('request', self.addressnamechange), (
        'json', '{"Address":"' + address + '","Name":"' + name + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def delete_address(self,address):
        payload = (('request', self.deladdress), (
        'json', '{"Address":"' + address + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        if result['Error'] != "Not a post valid request":
            self.status = False
            result = "Failed"
        return result

    def display_private_key(self,address):
        payload = (('request', self.displayprivatekey), (
        'json', '{"Address":"' + address + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def generate_new_factoid_address(self,name):
        payload = (('request', self.newfctaddress), (
        'json',  name))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def generate_new_entrycredit_address(self,name):
        payload = (('request', self.newecaddress), (
        'json', name))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def import_address_private_key(self,name,privatekey):
        payload = (('request', self.importaddress), (
        'json', '{"Name":"'+ name + ' ","Secret":"' + privatekey + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def import_koinify_address(self,name,koinify):
        payload = (('request', self.importkoinify), (
        'json', '{"Name":"' + name + '","Koinify":"' + koinify + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        return result

    def import_new_external_address(self,name,address):
        payload = (('request', self.newexternaladdress), (
        'json', '{"Name":"' + name + '","Public":"' + address + '"}'))
        result = self.enterprisewallet.send_post_request(payload)
        return result