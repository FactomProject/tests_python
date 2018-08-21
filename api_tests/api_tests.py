import unittest, re
from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.cli_methods import get_data_dump_from_nonansible_server
from helpers.helpers import read_data_from_json

import requests

@attr(fast=True)
class APITests(unittest.TestCase):
    data = read_data_from_json('addresses.json')
    shared_data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_api = APIObjectsFactomd()
        self.wallet_api = APIObjectsWallet()
        self.factomd_address = self.data['factomd_controlpanel']

    def test_directory_blocks(self):
        keymr = self.factom_api.get_directory_block_head()
        self.assertTrue('000000000000000000000000000000000000000000000000000000000000000a' ==
                        self.factom_api.get_directory_block_by_keymr(keymr)["entryblocklist"][0]['chainid'])

    def test_multiple_fct_balances(self):
        factoid_address2 = self.shared_data['factoid_address2']
        factoid_address3 = self.shared_data['factoid_address3']
        balances, lastsavedheight, currentheight = self.factom_api.multiple_fct__balances(factoid_address2, factoid_address3)

        # check balances
        actual_balance2 = self.factom_api.get_factoid_balance(factoid_address2)
        actual_balance3 = self.factom_api.get_factoid_balance(factoid_address3)
        self.assertTrue(balances[0]['ack'] == actual_balance2, 'ack balance for factoid address ' + self.shared_data['factoid_address2'] + ' not equal to actual balance ' + str(actual_balance2))
        self.assertTrue(balances[0]['saved'] == actual_balance2, 'saved balance for factoid address ' + self.shared_data['factoid_address2'] + ' not equal to actual balance ' + str(actual_balance2))
        self.assertTrue(balances[1]['ack'] == actual_balance3, 'ack balance for factoid address ' + self.shared_data['factoid_address3'] + ' not equal to actual balance ' + str(actual_balance3))
        self.assertTrue(balances[1]['saved'] == actual_balance3, 'saved balance for factoid address ' + self.shared_data['factoid_address3'] + ' not equal to actual balance ' + str(actual_balance3))

        # check heights
        directoryblockheight = self.factom_api.get_heights()['directoryblockheight']
        self.assertTrue(lastsavedheight == directoryblockheight, 'lastsavedheight ' + str(lastsavedheight) + ' does not match directory block height ' + str(directoryblockheight))
        self.assertTrue(currentheight == directoryblockheight + 1 or currentheight == directoryblockheight + 2, 'currentheight ' + str(currentheight) + ' is too far from directory block height ' + str(directoryblockheight))

    def test_multiple_ec_balances(self):
        entry_credit_address_public = self.shared_data['entry_credit_address_public']
        entry_credit_address_unknown = self.shared_data['entry_credit_address_unknown']
        balances, lastsavedheight, currentheight = self.factom_api.multiple_ec__balances(entry_credit_address_public, entry_credit_address_unknown)

        # check balances
        actual_balance_public = self.factom_api.get_entry_credit_balance(entry_credit_address_public)
        actual_balance_unknown = self.factom_api.get_entry_credit_balance(entry_credit_address_unknown)
        self.assertTrue(balances[0]['ack'] == actual_balance_public, 'ack balance for entry credit address ' + self.shared_data['entry_credit_address_public'] + ' not equal to actual balance ' + str(actual_balance_public))
        self.assertTrue(balances[0]['saved'] == actual_balance_public, 'ack balance for entry credit address ' + self.shared_data['entry_credit_address_public'] + ' not equal to actual balance ' + str(actual_balance_public))
        self.assertTrue(balances[1]['ack'] == actual_balance_unknown, 'ack balance for entry credit address ' + self.shared_data['entry_credit_address_unknown'] + ' not equal to actual balance ' + str(actual_balance_unknown))
        self.assertTrue(balances[1]['saved'] == actual_balance_unknown, 'ack balance for entry credit address ' + self.shared_data['entry_credit_address_unknown'] + ' not equal to actual balance ' + str(actual_balance_unknown))

        self.assertTrue(balances[1]['err'] == 'Address has not had a transaction', 'Unused ec address ' + self.shared_data['entry_credit_address_unknown'] + ' did not return error')
        directoryblockheight = self.factom_api.get_heights()['directoryblockheight']
        self.assertTrue(lastsavedheight == directoryblockheight, 'lastsavedheight ' + str(lastsavedheight) + ' does not match directory block height ' + str(directoryblockheight))
        self.assertTrue(currentheight == directoryblockheight + 1 or currentheight == directoryblockheight + 2, 'currentheight ' + str(currentheight) + ' is too far from directory block height ' + str(directoryblockheight))

    def test_get_heights(self):
        self.assertTrue('entryheight' in self.factom_api.get_heights())

    def test_get_blocks_by_heights(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        self.assertTrue('keymr' in self.factom_api.get_directory_block_by_height(directory_block_height))

    def test_get_current_minute(self):
        factomd_address_list = [self.data['factomd_address_0'], self.data['factomd_address_1'], self.data['factomd_address_2'], self.data['factomd_address_3'], self.data['factomd_address_4'], self.data['factomd_address_5'], self.data['factomd_address_6']]
        minute = []
        for factomd_address in factomd_address_list:
            datadump = get_data_dump_from_nonansible_server(self.factomd_address)
            datadumplist = datadump.split('/')
            temp = datadumplist[4]
            minute.append(int(re.search('[0-9]', temp).group()))
        self. assertTrue(all(x==minute[0] for x in minute), 'Not all nodes show the same minute' + str(minute))
        return minute[0]

    def test_get_factomd_properties(self):
        result = str(self.factom_api.get_factomd_properties())
        self.assertTrue('factomdversion' in result and 'factomdapiversion' in result, 'factomd properties command not working' )

    def test_get_wallet_properties(self):
        result = str(self.wallet_api.get_wallet_properties())
        self.assertTrue('walletversion' in result and 'walletapiversion' in result, 'wallet properties command not working' )

