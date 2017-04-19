import unittest
import time
from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack


@attr(checkheight=True)
class FactomTransactionBalanceTest(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    wallet = read_data_from_json('shared_test_data.json')
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address_0'],data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'],data['factomd_address_4'],
                                   data['factomd_address_5'],data['factomd_address_6'],data['factomd_address_7'],data['factomd_address_8'],data['factomd_address_9'],data['factomd_address_10'],]
    factomd_localhost = data['localhost']

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        #self.factom_cli_create.change_factomd_address(self.factomd_localhost)
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.wallet['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"'+self.wallet['words']+'"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.wallet['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def notest_make_transactions(self):
        value_of_factoids = 2
        #self.factom_cli_create.change_factomd_address(self.factomd_localhost)
        for i in range(0,1000):
            balance_1 = self.factom_cli_create.check_wallet_address_balance(self.third_address)
            text = self.factom_cli_create.send_factoids(self.first_address,self.third_address,str(value_of_factoids))
            chain_dict = self.factom_chain_object.parse_chain_data(text)
            tx_id = chain_dict['TxID']
            wait_for_ack(tx_id, 1)
            time.sleep(5)
            balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.third_address)
            self.assertEqual(float(balance_1_after), float(balance_1) + value_of_factoids)

    def notest_make_transactions_without_balance_check(self):
        value_of_factoids = 2
        #self.factom_cli_create.change_factomd_address(self.factomd_localhost)
        for i in range(0,1000):
            balance_1 = self.factom_cli_create.check_wallet_address_balance(self.third_address)
            text = self.factom_cli_create.send_factoids(self.first_address,self.third_address,str(value_of_factoids))


    def test_balance_on_nodes(self):
        #address_list = ["EC2RQiX72PtBcycDVPJDTo7WS6HcybT3uiYffoB77cdV9i1DvNrL"]
        address_list = ["FA3Y1tBWnFpyoZUPr9ZH51R1gSC8r5x5kqvkXL3wy4uRvzFnuWLB",
                        "FA3tS5Yem7c1WJ6iE1yF9dy98pXhjJLDP1hbLcSUn6w33rL2dRdD",
                        "FA2HDV33qbZgnYvzUu8raunaE4M8UBSwpE4MRmwTSVs9SyjYagXt",
                        "FA3qqkhBfpiPSSnZ8HhqWuJHXL7ZtdeSgPdKo5WjLv4AEedqFrcW",
                        "FA275GjfopyELGba7UyLnqLRieV4PAaFzFvnmaGNiXQ6f64CpHAo",
                        "FA3hKYiZZJQRnGBKtZwgKDS2FFP3MFRZNPW32hJeFyoFNbiCtacC",
                        "FA3dF6XV8kB46YH5C9yXC77qeUH2o7SSjgsTxVv1sEZZ9BXb9tHc",
                        "FA2e1Ga3MdUhorC5iG4x4HQ8kK3L6RGT4xzwkDsHjnih6U8SAXFY",
                        "EC2dmFatZhymujjfRTvoesTNgKES1AqTADBMD1JE1cu2CmqFRVbF",
                        "EC2DKSYyRcNWf7RS963VFYgMExoHRYLHVeCfQ9PGPmNzwrcmgm2r",
                        "FA2jK2HcLnRdS94dEcU27rF3meoJfpUcZPSinpb7AwQvPRY6RL1Q",
                        "EC1zpfdA5BjH6ixoYsu9KmYDrjDkqp1dX17nrgnWQ9Vsckh21Bbo",
                        "EC2RQiX72PtBcycDVPJDTo7WS6HcybT3uiYffoB77cdV9i1DvNrL",
                        "FA3EPZYqodgyEGXNMbiZKE5TS2x2J9wF8J9MvPZb52iGR78xMgCb",
                        "FA3Y1tBWnFpyoZUPr9ZH51R1gSC8r5x5kqvkXL3wy4uRvzFnuWLB",
                        "EC2RQiX72PtBcycDVPJDTo7WS6HcybT3uiYffoB77cdV9i1DvNrL"]

        #address = self.first_address
        for address in address_list:
            print "Address = %s" % address
            balance_1 = self.factom_cli_create.check_wallet_address_balance(address)
            print "Balance = %s of server = 10.41.0.5:8088" % balance_1
            for factomd_address_custom in self.factomd_address_custom_list:
                self.factom_cli_create.change_factomd_address(factomd_address_custom)
                balance_2 = self.factom_cli_create.check_wallet_address_balance(address)
                print "Balance = %s of server = %s" % (balance_2, factomd_address_custom)
                self.assertTrue(balance_1 == balance_2, "mismatch in balance. Balance of default server=%s, %s=%s, " % (balance_1, factomd_address_custom,balance_2))

    def notest_transactions_on_nodes(self):
        address_list = ["FA3EPZYqodgyEGXNMbiZKE5TS2x2J9wF8J9MvPZb52iGR78xMgCb",
                        "FA3Y1tBWnFpyoZUPr9ZH51R1gSC8r5x5kqvkXL3wy4uRvzFnuWLB"]

        #address = "EC2dmFatZhymujjfRTvoesTNgKES1AqTADBMD1JE1cu2CmqFRVbF"
        for address in address_list:
            print address
            transactions_1 = self.factom_cli_create.list_transactions_by_address(address)
            for factomd_address_custom in self.factomd_address_custom_list:
                self.factom_cli_create.change_factomd_address(factomd_address_custom)
                transactions_2 = self.factom_cli_create.list_transactions_by_address(address)
                self.assertTrue(transactions_1 == transactions_2, "mismatch in transactions. Transaction of default server=%s, %s=%s, " % (transactions_1, factomd_address_custom, transactions_2))

    def notest_list_addresses(self):
        self.factom_cli_create.change_factomd_address(self.factomd_address)
        list_address_1 = self.factom_cli_create.list_addresses()
        for factomd_address_custom in self.factomd_address_custom_list:
            self.factom_cli_create.change_factomd_address(factomd_address_custom)
            list_address_2 = self.factom_cli_create.list_addresses()
            self.assertTrue(list_address_1 == list_address_2, "mismatch in balances. check server %s" % factomd_address_custom)

