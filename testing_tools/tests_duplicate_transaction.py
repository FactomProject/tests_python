import unittest
import string
import random
import time

from nose.plugins.attrib import attr

from api_objects.api_objects_wallet import APIObjectsWallet
from api_objects.api_objects_factomd import APIObjectsFactomd
from helpers.helpers import read_data_from_json
from helpers.cli_methods import send_command_to_cli_and_receive_text

@attr(fast=True)
class ApiTestsDuplicateTransactions(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    _stop_factomd_command = 'pkill factomd'
    _start_factomd_command = 'factomd -count=6  -blktime=30  -network=LOCAL  > out_sim.txt'

    def setUp(self):
        self.wallet_api_objects = APIObjectsWallet()
        self.api_objects = APIObjectsFactomd()
        self.first_address = self.wallet_api_objects.import_address_by_secret(self.data['factoid_wallet_address'])
        self.second_address = self.wallet_api_objects.generate_factoid_address()
        self.entrycredit_address = self.wallet_api_objects.generate_ec_address()

    def test_duplicate_transactions(self):
        '''
        This testcase will submit 4 factoid transactions per second and checks for transaction status after one block time.
        :return: nothing. because the testcase only loads.
        special note  : this test case uses sleep to control the # of transaction input. waiting for acknowledgement causes ports to run out
            and test case fails
        '''
        #send_command_to_cli_and_receive_text(self._start_factomd_command)
        blocktime = self.data['BLOCKTIME']
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        self.api_objects.submit_factoid_by_transaction(transaction)
        time.sleep(blocktime)
        second_address_balance_1 = self.api_objects.get_factoid_balance_by_factoid_address(self.second_address)
        print self.second_address
        print second_address_balance_1
        send_command_to_cli_and_receive_text(self._stop_factomd_command)
        #time.sleep(30)
        #send_command_to_cli_and_receive_text(self._start_factomd_command)
        time.sleep(30)
        self.api_objects.submit_factoid_by_transaction(transaction)
        second_address_balance_2 = self.api_objects.get_factoid_balance_by_factoid_address(self.second_address)
        print second_address_balance_2
        self.assertTrue(second_address_balance_1 == second_address_balance_2,"Duplicate Transaction Found in address = %s"  % self.second_address)





