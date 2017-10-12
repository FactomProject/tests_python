import unittest

from nose.plugins.attrib import attr
from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd

from helpers.helpers import read_data_from_json


@attr(last=True)
class APITestsBalances(unittest.TestCase):

    def setUp(self):
        self.api_wallet_objects = APIObjectsWallet()
        self.api_objects = APIObjectsFactomd()
        self.address_list = []
        self.balance = 0
        self.total_balance = 0

    def test_all_addresses_balances_by_api(self):
        addresses = read_data_from_json('addresses.json')
        factomd_server_list = [addresses['factomd_address'], addresses['factomd_address_0'], addresses['factomd_address_1'],
                addresses['factomd_address_2'], addresses['factomd_address_3'], addresses['factomd_address_4'],
                addresses['factomd_address_5'], addresses['factomd_address_6']]

        wallet_addresses_raw = self.api_wallet_objects.check_all_addresses()
        wallet_addresses = [x['public'] for x in wallet_addresses_raw]

        for w_address in wallet_addresses:
            balance = []
            for address in factomd_server_list:
                self.api_objects.change_factomd_address(address)
                if 'FA' in w_address[:3]:
                    balance.append(self.api_objects.get_factoid_balance_by_factoid_address(w_address))
                else:
                    balance.append(self.api_objects.get_entry_credits_balance_by_ec_address(w_address))
                self.assertTrue(all(x == balance[0] for x in balance), "Wrong balance in address: " + w_address + "\n")

    @attr(production_tool=True)
    def test_negative_balances_mainnet(self):
        #testcase to check all the negative balances in production blockchain
        #steps- list all transactions
        #parse the output and fetch all the input and output addresses
        #verify the balance of all the addresses is not negative

        addresses = read_data_from_json('addresses.json')
        factomd_address = addresses['localhost']
        self.api_objects.change_factomd_address(factomd_address)
        listtxs =  self.api_wallet_objects.list_all_transactions_in_factoid_blockchain()
        count_transactions =  len(listtxs['transactions'])

        for i in range(0,count_transactions):
            if listtxs['transactions'][i]['inputs']:
                count_inputs = len(listtxs['transactions'][i]['inputs'])
                for j in range(0,count_inputs):
                    input_address = listtxs['transactions'][i]['inputs'][j]['address']
                    if (self.check_if_exists(self.address_list,input_address) != True):
                        self.add_balance(input_address)
                        self.assertFalse(self.balance < 0,"negative balance found. Address %s, balance %s" % (input_address, self.balance))

            if listtxs['transactions'][i]['outputs']:
                count_outputs = len(listtxs['transactions'][i]['outputs'])
                for j in range(0,count_outputs):
                    output_address = listtxs['transactions'][i]['outputs'][j]['address']
                    if (self.check_if_exists(self.address_list, output_address) != True):
                        self.add_balance(output_address)
                        self.assertFalse(self.balance < 0,"negative balance found. Address %s, balance %s" % (output_address, self.balance))

        #check if total balance is more than what we gave away in round one ie. 8.7 million
        #divide to fetch factoids and then convert to millions
        factoids =  self.total_balance/100000000000000
        self.assertFalse(factoids > 8.8, "CRITICAL: Factoids has increased in the blockchain")

    def check_if_exists(self,addresslist,uniq_address):
        for address in addresslist:
            if address == uniq_address:
                return True


    def add_balance(self,address):
        self.address_list.append(address)
        self.balance = self.api_objects.get_factoid_balance_by_factoid_address(address)
        self.total_balance = self.total_balance + self.balance
        return self.balance