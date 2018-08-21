import unittest, string, random, time, os, json

from flaky import flaky
from nose.plugins.attrib import attr

from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet
from helpers.helpers import read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class ApiTestsWallet(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')
    blocktime = int(os.environ['BLOCKTIME'])
    WAITTIME = 300

    def setUp(self):
        self.api_objects = APIObjectsFactomd()
        self.wallet_api_objects = APIObjectsWallet()
        public_keys = self.wallet_api_objects.import_addresses(
            self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        self.first_address = public_keys[0]
        self.entry_creds_wallet = public_keys[1]
        self.second_address = self.wallet_api_objects.generate_factoid_address()
        self.entry_creds_wallet2 = self.wallet_api_objects.generate_ec_address()

    def test_allocate_funds_to_factoid_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        result = self.api_objects.submit_factoid_by_transaction(transaction)
        self.assertIn("Successfully submitted", result['message'], 'Factoid transaction not successful')
        # TODO insert code here (or somewhere) to test api_objects.get_transaction_by_hash after designers have decided on how exactly it should work
        # self. api_objects.get_transaction_by_hash(result['txid'])
        # self. api_objects.get_transaction_by_hash('b75e4d082b0921e744ea351b46fbfb369e00c2e04bc0cf9f834787d58c33df6b')

        # chain id for factoid transaction is always 000...f, abbreviated to just f
        for x in range(0, 300):
            status = self.api_objects.get_status(result['txid'], 'f')['status']
            if (status == 'TransactionACK'):
                break
            time.sleep(1)
        self.assertLess(x, 299, 'Factoid transaction not acknowledged within 5 minutes')
        self.wallet_api_objects.list_transactions_by_txid(result['txid'])


    def test_allocate_not_enough_funds(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))


        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 1)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 1)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)

        self.assertTrue('Error totalling Outputs: Amount is out of range' in
                        self.wallet_api_objects.sign_transaction(transaction_name)['error']['data'])

    def test_list_transactions_api_call(self):
        self.wallet_api_objects.list_all_transactions_in_factoid_blockchain()

    def test_list_transaction_by_id(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_output_to_transaction(transaction_name, self.second_address, 100000000)
        self.wallet_api_objects.subtract_fee_from_transaction(transaction_name, self.second_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        txid = self.api_objects.submit_factoid_by_transaction(transaction)['txid']
        wait_for_ack(txid)
        self.assertTrue(self.wallet_api_objects.list_transactions_by_txid(txid)[0]['inputs'][0]['amount'] == 100000000, 'Transaction is not listed')

    def test_list_current_working_transactions_in_wallet(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

    def test_delete_transaction(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range(5))

        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.assertTrue(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

        self.wallet_api_objects.delete_transaction(transaction_name)
        self.assertFalse(transaction_name in self.wallet_api_objects.list_current_working_transactions_in_wallet())

    def test_allocate_funds_to_ec_wallet_address(self):
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))
        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_entry_credit_output_to_transaction(transaction_name, self.entry_creds_wallet, 100000000)
        self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)
        tx_id = self.api_objects.submit_factoid_by_transaction(transaction)['txid']
        self.assertIn("Successfully submitted", self.api_objects.submit_factoid_by_transaction(transaction)['message'], "Transaction failed")
        for x in range(0, self.blocktime):
            pending = self.api_objects.get_pending_transactions(self.first_address)
            if 'TransactionACK' in str(pending) and tx_id in str(pending): break
            time.sleep(0.25)
        self.assertLess(x, self.blocktime, 'Transaction never pending')

    def test_import_12_words(self):
        self.wallet_api_objects.import_mnemonic(self.data['words'])

    def test_wallet_balances(self):
        factoid_total_ack = 0
        factoid_total_saved = 0
        entry_credit_total_ack = 0
        entry_credit_total_saved = 0
        for address in self.wallet_api_objects.check_all_addresses():
            if address['public'][0] == 'F':
                factoid_total_ack += self.api_objects.multiple_fct__balances(address['public'])[0][0]['ack']
                factoid_total_saved += self.api_objects.multiple_fct__balances(address['public'])[0][0]['saved']
            elif address['public'][0] == 'E':
                entry_credit_total_ack += self.api_objects.multiple_ec__balances(address['public'])[0][0]['ack']
                entry_credit_total_saved += self.api_objects.multiple_ec__balances(address['public'])[0][0]['saved']
            else: self.assertTrue(False, 'Address neither factoid nor entry credit')
        fctaccountbalances, ecaccountbalances = self.wallet_api_objects.wallet_balances()
        self.assertTrue(fctaccountbalances['ack'] == factoid_total_ack, 'factoid ack total ' + str(
            fctaccountbalances['ack']) + ' does not match total of all wallet factoid addresses ' + str(factoid_total_ack))
        self.assertTrue(fctaccountbalances['saved'] == factoid_total_saved, 'factoid saved total ' + str(
            fctaccountbalances['ack']) + ' does not match total of all wallet factoid addresses ' + str(factoid_total_saved))
        self.assertTrue(ecaccountbalances['ack'] == entry_credit_total_ack, 'entry credit ack total ' + str(
            ecaccountbalances['ack']) + ' does not match total of all wallet entry credit addresses ' + str(
            entry_credit_total_ack))
        self.assertTrue(ecaccountbalances['ack'] == entry_credit_total_saved, 'entry credit saved total ' + str(
            ecaccountbalances['ack']) + ' does not match total of all wallet entry credit addresses ' + str(
            entry_credit_total_saved))

    def test_ack_balance_vs_saved_balance(self):
        # create entry credit transaction
        transaction_name = ''.join(random.choice(string.ascii_letters) for _ in range (5))
        self.wallet_api_objects.create_new_transaction(transaction_name)
        self.wallet_api_objects.add_input_to_transaction(transaction_name, self.first_address, 100000000)
        self.wallet_api_objects.add_entry_credit_output_to_transaction(transaction_name, self.entry_creds_wallet, 100000000)
        self.wallet_api_objects.add_fee_to_transaction(transaction_name, self.first_address)
        self.wallet_api_objects.sign_transaction(transaction_name)
        transaction = self.wallet_api_objects.compose_transaction(transaction_name)

        # wait for minute 0
        for seconds in range(0, self.WAITTIME):
            minute = self.api_objects.get_current_minute()['minute']
            if minute == 0: break
            time.sleep(1)
        self.assertEqual(minute, 0, 'Minute 0 never happened')

        # submit transaction
        tx_id = self.api_objects.submit_factoid_by_transaction(transaction)['txid']
        self.assertIn("Successfully submitted", self.api_objects.submit_factoid_by_transaction(transaction)['message'], "Transaction failed")

        for seconds in range(0, self.WAITTIME):
            minute = self.api_objects.get_current_minute()['minute']
            fctaccountbalances, ecaccountbalances = self.wallet_api_objects.wallet_balances()
            if minute == 9: break
            time.sleep(1)
        self.assertEqual(minute, 9, 'Minute 9 never happened')

        for seconds in range(0, self.WAITTIME):
            minute = self.api_objects.get_current_minute()['minute']
            fctaccountbalances, ecaccountbalances = self.wallet_api_objects.wallet_balances()
            if minute == 5: break
            time.sleep(1)
        self.assertEqual(minute, 5, 'Minute 5 never happened')



