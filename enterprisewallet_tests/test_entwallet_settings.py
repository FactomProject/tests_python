from enterprisewallet_objects.entwallet_settings_objects import EnterpriseWalletSettingsObjects
from api_objects.factomd_api_objects import FactomApiObjects
import unittest
from helpers.helpers import read_data_from_json

from nose.plugins.attrib import attr

@attr(fast=True)
class EnterpriseWalletSettingsTests(unittest.TestCase):

    def setUp(self):
        self.entwallet_settings_objects = EnterpriseWalletSettingsObjects()
        self.factom_api = FactomApiObjects()
        data = read_data_from_json('addresses.json')
        self.factomdaddress = data['factomd_address']
        self.factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                       data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                       data['factomd_address_6']]

    def test_get_status_enterprise_wallet(self):
        result = self.entwallet_settings_objects.get_status_enterprise_wallet()
        self.assertTrue(result['Error'] == 'none',"Enterprise Wallet is not up")

    def test_check_synched_status(self):
        result = self.entwallet_settings_objects.get_synched_status()
        self.assertTrue(result['Error'] == 'none', "Enterprise Wallet is not synced")
        result_1 = self.factom_api.get_heights()
        self.assertTrue(result['Content']['LeaderHeight'] == result_1['leaderheight'],"Wallet has not fully synced")

    def test_adjust_settings_to_all_false(self):
        values = ["false","false","false","false"]
        result = self.entwallet_settings_objects.set_adjust_settings(values,self.factomdaddress)
        self.assertTrue(result['Error'] == 'none',"Settings not saved")

    def test_adjust_settings_to_all_true(self):
        values = ["true", "true", "true", "true"]
        result = self.entwallet_settings_objects.set_adjust_settings(values, self.factomdaddress)
        self.assertTrue(result['Error'] == 'none', "Settings not saved")

    def test_adjust_settings_to_various_values(self):
        values = ["true","false","false","true"]
        result = self.entwallet_settings_objects.set_adjust_settings(values,self.factomdaddress)
        self.assertTrue(result['Error'] == 'none', "Settings not saved")

    def test_adjust_settings_to_various_factomd(self):
        values = ["true","true","true","true"]
        for factomd_address_custom in self.factomd_address_custom_list:
            result = self.entwallet_settings_objects.set_adjust_settings(values,factomd_address_custom)
            #print result
            self.assertTrue(result['Error'] == 'none', "Settings not saved")
        #set the wallet to valid address, after testing
        self.entwallet_settings_objects.set_adjust_settings(values, self.factomdaddress)

    def notest_adjust_settings_to_invalid_factomd(self):
        values = ["true","true","true","true"]
        result = self.entwallet_settings_objects.set_adjust_settings(values,"10.0.0.1:8088")
        self.assertTrue(result['Error'] == 'none', "Settings not saved")
        #verify if the wallet synces with the invalid address.If it does, then we have a problem
        result = self.entwallet_settings_objects.get_synched_status()
        self.assertTrue(result['Content']['Synced'] == False,"Enterprise Wallet accepts invalid ip address!")
        #set the wallet to valid address, after testing
        self.entwallet_settings_objects.set_adjust_settings(values, self.factomdaddress)

