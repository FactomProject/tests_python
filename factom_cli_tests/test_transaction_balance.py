import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_chain_objects import FactomChainObjects
from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from helpers.general_test_methods import wait_for_ack
from helpers.helpers import read_data_from_json
from helpers.loadnodes import LoadNodes


@attr(load=True)
class FactomTransactionBalanceTest(unittest.TestCase):
    '''
    testcases to verify balances and transactions are the same in every node in the network
    '''
    wallet = read_data_from_json('shared_test_data.json')
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'],data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'],data['factomd_address_4'],
                                   data['factomd_address_5'],data['factomd_address_6']]

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.wallet['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.factom_load_nodes = LoadNodes()

    def notest_make_transactions(self):
        value_of_factoids = 2
        for i in range(0,1200):
            balance_1 = self.factom_cli_create.check_wallet_address_balance(self.second_address)
            text = self.factom_cli_create.send_factoids(self.first_address,self.second_address,str(value_of_factoids))
            chain_dict = self.factom_chain_object.parse_chain_data(text)
            tx_id = chain_dict['TxID']
            wait_for_ack(tx_id,5)
            balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.second_address)
            self.assertEqual(float(balance_1_after), float(balance_1) + value_of_factoids)
        self.balance_on_nodes()
        self.transactions_on_nodes()

    def test_make_transactions_no_ack(self):
        value_of_factoids = 2
        for i in range(0,1200):
            balance_1 = self.factom_cli_create.check_wallet_address_balance(self.second_address)
            text = self.factom_cli_create.send_factoids(self.first_address,self.second_address,str(value_of_factoids))
        self.balance_on_nodes()
        self.transactions_on_nodes()


    def balance_on_nodes(self):
        address_list = [self.first_address,
                        self.second_address]
        status = self.factom_load_nodes.balance_on_nodes(address_list)
        self.assertTrue(status == False, "Balance mismatch. Testcase failed")

    def transactions_on_nodes(self):
        address_list = [self.first_address,
                        self.second_address]
        status = self.factom_load_nodes.transactions_on_nodes(address_list)
        self.assertTrue(status == False, "Balance mismatch. Testcase failed")

    def notest_transactions_on_nodes(self):
        listaddress_1 = self.factom_cli_create.list_addresses()
        for factomd_address_custom in self.factomd_address_custom_list:
            self.factom_cli_create.change_factomd_address(factomd_address_custom)
            listaddress_2 = self.factom_cli_create.list_addresses()
            if (listaddress_1 != listaddress_2):
                self.assertTrue(listaddress_1 == listaddress_2,"mismatch in listaddress.server %s "  % (factomd_address_custom))


