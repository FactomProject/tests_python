from helpers.helpers import read_data_from_json
from enterprisewallet_objects.entwallet_objects import EnterpriseWalletObjects

class EnterpriseWalletSettingsObjects():

    def __init__(self):
        self.entwallet_objects = EnterpriseWalletObjects()
        self.synced = 'synced'
        self.online = 'on'
        self.status = True
        self.adjustsetting = 'adjust-settings'
        self.getseed = 'get-seed'


    def get_synched_status(self):
        result = self.entwallet_objects.send_get_request(self.synced)
        return result

    def get_status_enterprise_wallet(self):
        result = self.entwallet_objects.send_get_request(self.online)
        return result

    def set_adjust_settings(self,settings,address):
        value_str = ""
        for settings_value in settings:
            value_str = value_str + "," + settings_value
        value_str = value_str.lstrip(",")
        payload = (('request', self.adjustsetting), (
        'json', '{"Values":[' + value_str + '],"FactomdLocation":"' + address + '"}'))
        result = self.entwallet_objects.send_post_request(payload)
        return result

    def get_seed(self,seed):
        if seed != "":
            payload = (('request', self.getseed), (
        'json', '{"Seed":"' + seed + '"}'))
        result = self.entwallet_objects.send_post_request(payload)
        return result


