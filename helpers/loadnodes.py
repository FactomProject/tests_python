
import os
import time
import logging
from general_test_methods import wait_for_ack
from helpers import create_random_string
from random import randint
from cli_objects.factom_chain_objects import FactomChainObjects
from cli_objects.factom_cli_create import FactomCliCreate
from helpers import read_data_from_json


class LoadNodes():

    def __init__(self):
        self.factom_cli_create = FactomCliCreate()
        self.factom_chain_object = FactomChainObjects()
        data = read_data_from_json('addresses.json')

        self.factomd_address_custom_list = [data['factomd_address'], data['factomd_address_0'], data['factomd_address_1'],
                                       data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'],
                                       data['factomd_address_5'], data['factomd_address_6']]

    def make_chain_and_check_balance(self,address_list):
        first_address = address_list[0]
        entry_creds_wallet2 = address_list[1]
        chain_flags_list = ['-C ']
        for i in xrange(10):
            #path = os.path.join(os.path.dirname(__file__), '../test_data/testfile')
            tx_id = self.factom_cli_create.buy_ec_return_tx_id(first_address, entry_creds_wallet2, '1000')
            #time.sleep(10)
            wait_for_ack(tx_id,10)
            for i in range(10):
                with open('output_file', 'wb') as fout:
                    fout.write(os.urandom(randint(100, 5000)))
                    path = fout.name
                name_1 = create_random_string(5)
                name_2 = create_random_string(5)
                names_list = ['-n', name_1, '-n', name_2]
                chain_id = self.factom_chain_object.make_chain_from_binary(entry_creds_wallet2, path, names_list,flag_list=chain_flags_list)
                fout.close()
                for i in range(10):
                    with open('output_file', 'wb') as fout:
                        fout.write(os.urandom(randint(100, 5000)))
                        path = fout.name
                    name_1 = create_random_string(5)
                    name_2 = create_random_string(5)
                    names_list = ['-e', name_1, '-e', name_2]
                    self.factom_chain_object.add_entries_to_chain(entry_creds_wallet2, path, chain_id, names_list)
                    fout.close()
                    if os._exists(path):
                        os.remove(path)
                    time.sleep(1)
                time.sleep(1)
                self.fetch_entries_with_chainid(chain_id)
            time.sleep(1)
            self.balance_on_nodes([first_address,entry_creds_wallet2])
            self.transactions_on_nodes([first_address,entry_creds_wallet2])


    def balance_on_nodes(self,address_list):
        for address in address_list:
            balance_1 = self.factom_cli_create.check_wallet_address_balance(address)
            for factomd_address_custom in address_list:
                self.factom_cli_create.change_factomd_address(factomd_address_custom)
                balance_2 = self.factom_cli_create.check_wallet_address_balance(address)
                if (balance_1 != balance_2):
                    logging.getLogger('cli_command').info("mismatch in balance. Balance of default server=%s, but server %s=%s, address = %s " % (balance_1, factomd_address_custom,balance_2,address))
                    return False
            return True


    def transactions_on_nodes(self,address_list):
        for address in address_list:
            transactions_1 = self.factom_cli_create.list_transactions_by_address(address)
            for factomd_address_custom in address_list:
                self.factom_cli_create.change_factomd_address(factomd_address_custom)
                transactions_2 = self.factom_cli_create.list_transactions_by_address(address)
                if (transactions_1 == transactions_2):
                    logging.getLogger('cli_command').info("mismatch in transactions. Transaction of default server=%s, %s=%s" % (transactions_1, factomd_address_custom, transactions_2))
                    return False
            return True

    def fetch_entries_with_chainid(self,chain_id):
        print chain_id
        for factomd_address_custom in self.factomd_address_custom_list:
            self.factom_cli_create.change_factomd_address(factomd_address_custom)
            allentries_output = self.factom_chain_object.get_allentries(chain_id)
            if (allentries_output.find("Entry [10]")):
                print "found 11 entries in server - %s" %factomd_address_custom
            else:
                print "all entries are not available in the server - %s" %factomd_address_custom




