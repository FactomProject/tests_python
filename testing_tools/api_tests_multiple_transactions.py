import unittest, string, random, time

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json

@attr(load=True)
class ApiTestsTransactions(unittest.TestCase):
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.first_address = self.api_wallet.import_addresses(self.data['factoid_wallet_address'])[0]
        self.second_address = self.api_wallet.generate_factoid_address()
        self.entrycredit_address = self.api_wallet.generate_ec_address()

    def test_multiple_factoid_address_transactions(self):
        '''
        This testcase will submit 4 factoid transactions per second and checks for transaction status after one block time.
        :return: nothing. because the testcase only loads.
        special note  : this test case uses sleep to control the # of transaction input. waiting for acknowledgement causes ports to run out
            and test case fails
        '''
        blocktime = self.blocktime
        txidlist = []
        for x in range(1,6000):
            for temp in range(1,blocktime):
                for y in range(1,5):
                    transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
                    self.api_wallet.create_new_transaction(transaction_name)
                    self.api_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
                    self.api_wallet.add_output_to_transaction(transaction_name, self.second_address, 100000000)
                    self.api_wallet.add_fee_to_transaction(transaction_name, self.first_address)
                    self.api_wallet.sign_transaction(transaction_name)
                    transaction = self.api_wallet.compose_transaction(transaction_name)
                    txidlist.append(self.api_factomd.submit_factoid_by_transaction(transaction)['txid'])
                time.sleep(1)
            time.sleep(blocktime)
            for txid in txidlist:
                status = self.api_factomd.get_status(txid,'f')['status']
                self.assertEquals(status, 'DBlockConfirmed', 'Transaction = %s is still not confirmed' % txid)

    def test_multiple_entrycredit_address_transactions(self):
        '''
        This testcase will submit 4 entry credit transactions per second and checks for transaction status after one block time.
        return: nothing.  because the testcase only loads.
        special note  : this test case uses sleep to control the # of transaction input. waiting for acknowledgement causes ports to run out
            and test case fails
        '''
        blocktime = self.blocktime
        txidlist = []
        count = 0
        for x in range(1, 6000):
            for temp in range(1, blocktime):
                for y in range(1, 5):
                    transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))
                    self.api_wallet.create_new_transaction(transaction_name)
                    example = self.api_wallet.add_input_to_transaction(transaction_name, self.first_address, 100000000)
                    self.api_wallet.add_entry_credit_output_to_transaction(transaction_name, self.entrycredit_address, 100000000)
                    self.api_wallet.add_fee_to_transaction(transaction_name, self.first_address)
                    self.api_wallet.sign_transaction(transaction_name)
                    transaction = self.api_wallet.compose_transaction(transaction_name)
                    txidlist.append(self.api_factomd.submit_factoid_by_transaction(transaction)['txid'])
                time.sleep(1)
            time.sleep(blocktime)
            for txid in txidlist:
                count += 1
                status = self.api_factomd.get_status(txid, 'f')['status']
                self.assertEquals(status, 'DBlockConfirmed', 'Transaction = %s is still not confirmed' % txid)
