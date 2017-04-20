import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from api_objects.factomd_api_objects import FactomApiObjects

from helpers.helpers import read_data_from_json

@attr(last=True)
class FactomChainTests(unittest.TestCase):

    def setUp(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        self.factomd_api_objects = FactomApiObjects()

    def test_all_addresses_balances(self):
        """
        tests all addresses in wallet and all balances on servers
        :return:
        """
        addresses = read_data_from_json('addresses.json')
        list = [addresses['factomd_address'], addresses['factomd_address_0'], addresses['factomd_address_1'],
                addresses['factomd_address_2'], addresses['factomd_address_3'], addresses['factomd_address_4'],
                addresses['factomd_address_5'], addresses['factomd_address_6']]

        wallet_addresses_raw = self.factom_cli_create.list_addresses()
        wallet_addresses_list = [x.split(' ')[0] for x in wallet_addresses_raw.split("\n")]

        for w_address in wallet_addresses_list:
            balance = []
            for address in list:
                self.factom_cli_create.change_factomd_address(address)
                balance.append(self.factom_cli_create.check_wallet_address_balance(w_address))
                self.assertTrue(all(x == balance[0] for x in balance), "Wrong balance in address: " + w_address + "\n")
                self.assertTrue(balance[0] > 0)



