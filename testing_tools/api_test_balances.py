import unittest

from nose.plugins.attrib import attr
from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd

from helpers.helpers import read_data_from_json

@attr(last=True)
class CLITestsBalances(unittest.TestCase):

    def setUp(self):
        self.api_wallet_objects = APIObjectsWallet()
        self.api_objects = APIObjectsFactomd()

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
