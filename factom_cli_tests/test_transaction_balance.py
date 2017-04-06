import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json, wait_for_ack


@attr(checkheight=True)
class FactomTransactionBalanceTest(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    wallet = read_data_from_json('shared_test_data.json')
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address'], data['factomd_address_0'], data['factomd_address_1'],
                                   data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'],
                                   data['factomd_address_5'],
                                   data['factomd_address_6'], data['factomd_address_7'], data['factomd_address_8'],
                                   data['factomd_address_9'], data['factomd_address_10']]

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.wallet['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"'+self.wallet['words']+'"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_factom_change_entry_credit_conversion_rate()
        self.entry_creds_wallet1 = self.factom_cli_create.import_address_from_factoid(
            self.wallet['ec_wallet_address'])
        self.entry_creds_wallet2 = self.factom_cli_create.create_entry_credit_address()

    def notest_make_transactions(self):
        value_of_factoids = 1
        for i in range(0,100):
            balance_1 = self.factom_cli_create.check_wallet_address_balance(self.second_address)
            text = self.factom_cli_create.send_factoids(self.first_address,self.second_address,str(value_of_factoids))
            chain_dict = self.factom_chain_object.parse_chain_data(text)
            tx_id = chain_dict['TxID']
            wait_for_ack(self,tx_id, 1)
            balance_1_after = self.factom_cli_create.check_wallet_address_balance(self.second_address)
            self.assertEqual(int(balance_1_after), int(balance_1) + value_of_factoids)

    def test_balance_on_nodes(self):
        address_list = ["FA2e1Ga3MdUhorC5iG4x4HQ8kK3L6RGT4xzwkDsHjnih6U8SAXFY",
                        "EC2dmFatZhymujjfRTvoesTNgKES1AqTADBMD1JE1cu2CmqFRVbF",
                        "EC2DKSYyRcNWf7RS963VFYgMExoHRYLHVeCfQ9PGPmNzwrcmgm2r",
                        "FA2jK2HcLnRdS94dEcU27rF3meoJfpUcZPSinpb7AwQvPRY6RL1Q",
                        "EC1zpfdA5BjH6ixoYsu9KmYDrjDkqp1dX17nrgnWQ9Vsckh21Bbo",
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
                        "EC2dmFatZhymujjfRTvoesTNgKES1AqTADBMD1JE1cu2CmqFRVbF",
                        "EC2DKSYyRcNWf7RS963VFYgMExoHRYLHVeCfQ9PGPmNzwrcmgm2r",
                        "FA2jK2HcLnRdS94dEcU27rF3meoJfpUcZPSinpb7AwQvPRY6RL1Q",
                        "EC1zpfdA5BjH6ixoYsu9KmYDrjDkqp1dX17nrgnWQ9Vsckh21Bbo"]

        #address = "EC2dmFatZhymujjfRTvoesTNgKES1AqTADBMD1JE1cu2CmqFRVbF"
        for address in address_list:
            print address
            transactions_1 = self.factom_cli_create.list_transactions_by_address(address)
            for factomd_address_custom in self.factomd_address_custom_list:
                self.factom_cli_create.change_factomd_address(factomd_address_custom)
                transactions_2 = self.factom_cli_create.list_transactions_by_address(address)
                self.assertTrue(transactions_1 == transactions_2, "mismatch in transactions. Transaction of default server=%s, %s=%s, " % (transactions_1, factomd_address_custom, transactions_2))



