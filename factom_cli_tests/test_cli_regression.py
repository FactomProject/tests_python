import unittest
import json
import re
from nose.plugins.attrib import attr

from cli_objects.factom_cli_objects import FactomCliMainObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class FactomCliEndToEndTest(unittest.TestCase):
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        self.factom_cli_create = FactomCliMainObjects()
        self.factom_chain_object = FactomChainObjects()
        self.first_address = self.factom_cli_create.import_address_from_factoid(self.data['factoid_wallet_address'])
        self.second_address = self.factom_cli_create.create_new_factoid_address()
        words = '"'+self.data['words']+'"'
        self.third_address = self.factom_cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.factom_cli_create.get_entry_credit_rate()
        self.entry_credit_address = self.factom_cli_create.import_address_from_factoid(
            self.data['ec_wallet_address'])

    def test_raw_blocks(self):

        # find a directory block with entries
        block_height = 0
        head_height = int(self.factom_chain_object.get_directory_block_height_from_head())
        for x in range(0, head_height):
            dblock = json.loads(self.factom_chain_object.get_directory_block_by_height(x))
            entries = len(dblock['dblock']['dbentries'])
            if entries > 3:
                block_height = x
                break
        self.assertNotEquals(block_height, 0, 'Network has no identities')

        # directory block raw data
        dhash=dblock['dblock']['dbhash']
        self.assertEquals(dblock['rawdata'], self.factom_chain_object.get_raw(dhash), 'Incorrect raw data fetched for Directory Block at height ' + str(block_height))

        # entry block raw data
        # ENTRY = 3 skips over administrative entries
        ENTRY = 3
        keyMR = dblock['dblock']['dbentries'][ENTRY]['keymr']
        eblock = self.factom_chain_object.get_entry_block(keyMR)
        self.assertIn(self.factom_chain_object.parse_block_data(eblock)['EBEntry'][0]['EntryHash'], self.factom_chain_object.get_raw(keyMR), 'Incorrect raw data fetched for Entry Block at height ' + str(block_height))

        # admin block raw data
        ablock=json.loads(self.factom_chain_object.get_admin_block_by_height(block_height))
        ahash=ablock['ablock']['backreferencehash']
        self.assertEquals(ablock['rawdata'], self.factom_chain_object.get_raw(ahash), 'Incorrect raw data fetched for Admin Block at height ' + str(block_height))

        # TODO Once factomd get ecbheight code is corrected, insert correct hash field and activate this test

        # entry credit block raw data
        # ecblock=json.loads(self.factom_chain_object.get_entrycredit_block_by_height(block_height))
        # echash=ecblock['ecblock']['header']['????hash']
        # self.assertEquals(ecblock['rawdata'], self.factom_chain_object.get_raw(echash), 'Incorrect raw data fetched for Entry Credit Block at height ' + str(block_height))

        # factoid block raw data
        fblock=json.loads(self.factom_chain_object.get_factoid_block_by_height(block_height))
        fhash=fblock['fblock']['keymr']
        self.assertEquals(fblock['rawdata'], self.factom_chain_object.get_raw(fhash), 'Incorrect raw data fetched for Factoid Block at height ' + str(block_height))

    def test_allocate_funds_to_factoid_wallet_address_quiet_output(self):
        AMOUNT_SENT = 1
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address,
                                                                str(AMOUNT_SENT))

        # test add_output_to_transaction_quiet_flag
        factom_flags_list = ['-q']
        self.factom_cli_create.add_factoid_output_to_transaction(transaction_name, self.second_address, str(AMOUNT_SENT), flag_list=factom_flags_list)

        # check that output was added
        text = self.factom_cli_create.subtract_fee_from_transaction_output(transaction_name, self.second_address)
        transaction_dict = self.factom_chain_object.parse_transaction_data(text)
        self.assertEqual(str(AMOUNT_SENT - float(self.ecrate) * 12), transaction_dict['TotalOutputs'], "Quiet output not accepted")
        self.factom_cli_create.sign_transaction(transaction_name)

        # compose transaction
        self.assertTrue('curl' and 'transaction' in self.factom_cli_create.compose_transaction(transaction_name), "Curl command not created")

        # send transaction
        text = self.factom_cli_create.send_transaction(transaction_name)

        # check for pending transaction
        self.factom_chain_object.get_pending_transactions()
        # TODO When get_pending_transactions code is repaired, insert assert code here that verifies its proper functioning

        chain_dict = self.factom_chain_object.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)

        self.assertNotEqual(self.factom_cli_create.check_wallet_address_balance(self.second_address), 0, 'Factoids were not send to address: ' + self.second_address)

    def test_if_you_can_compose_wrong_transaction(self):
        self.assertIn("Transaction name was not found", self.factom_cli_create.compose_transaction('not_existing_trans'), 'Non-existent transaction was found in wallet')

    def test_request_balance_wrong_account(self):
        self.assertIn('Undefined or invalid address', self.factom_cli_create.check_wallet_address_balance(
            'Non-existent address'),'Non-existent address is showing up')

    def test_entry_credits_wallet(self):
        self.assertIn(self.entry_credit_address, self.factom_cli_create.export_addresses(), 'Not all addresses were exported')
        self.assertIn(self.entry_credit_address, self.factom_cli_create.list_addresses(), 'Not all addresses '
                                                                                                  'were listed')

    def test_create_transaction_with_no_inputs_outputs_or_entry_creds(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.assertIn('Insufficient Fee', self.factom_cli_create.sign_transaction(transaction_name))
        self.assertIn('Cannot send unsigned transaction', self.factom_cli_create.send_transaction(transaction_name))

    def test_delete_transaction(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, '1')
        self.factom_cli_create.add_factoid_output_to_transaction(transaction_name, self.second_address, '1')
        self.factom_cli_create.subtract_fee_from_transaction_output(transaction_name, self.second_address)
        self.assertIn(transaction_name, self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertNotIn(transaction_name, self.factom_cli_create.list_local_transactions(), 'Transaction was not deleted')

    def test_create_transaction_with_not_equal_input_and_output(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, '1')
        self.assertIn("Inputs and outputs don't add up",
                        self.factom_cli_create.subtract_fee_from_transaction_output(transaction_name, self.first_address), "Input and output don't add up, but error is not displayed")
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertNotIn(transaction_name, self.factom_cli_create.list_local_transactions(),
                        'Transaction was not deleted')

    def test_add_input_larger_than_10x_fee_to_correct_transaction_quiet_input(self):
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)

        # test add_input_to_transaction_quiet_flag
        factom_flags_list = ['-q']
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, '1', flag_list=factom_flags_list)

        # check that input was added
        text = self.factom_cli_create.add_factoid_output_to_transaction(transaction_name, self.first_address,
                                                                               '1')
        dict = self.factom_chain_object.parse_transaction_data(text)
        self.assertEqual('1', dict['TotalInputs'], "Quiet input not accepted")

        self.factom_cli_create.subtract_fee_from_transaction_output(transaction_name, self.first_address)

        # try to overpay
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, '10')
        self.assertIn('Overpaying fee', self.factom_cli_create.sign_transaction(transaction_name),
                        'Was able to overpay fee')
        self.factom_cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertNotIn(transaction_name, self.factom_cli_create.list_local_transactions(),
                        'Transaction was not removed')

    def test_create_transaction_with_no_output_or_ec(self):
        balance_before = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, '1')

        # new input from same address should overwrite 1st input
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, str(format(float(self.ecrate) * 8, 'f')))

        self.factom_cli_create.sign_transaction(transaction_name)
        self.assertIn(transaction_name, self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        self.factom_cli_create.send_transaction(transaction_name)

        # check for pending transaction return transaction id
        factom_flags_list = ['-T']
        self.factom_chain_object.get_pending_transactions(flag_list=factom_flags_list)

        # TODO When get_pending_transactions code is repaired, insert code here that verifies its proper functioning

        balance_after = self.factom_cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(abs(float(balance_after) - (float(balance_before) - float(self.ecrate) * 8)) <= 0.0000001, 'Balance is not subtracted correctly')

    def test_create_transaction_with_input_to_ec_quiet_addfee(self):
        FACTOID_AMOUNT = 1

        balance_before = self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address)
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address, str(FACTOID_AMOUNT))
        self.factom_cli_create.add_entry_credit_output_to_transaction(transaction_name,
                                                                      self.entry_credit_address, str(FACTOID_AMOUNT))

        # test add_fee_to_transaction quiet flag
        factom_flags_list = ['-q']
        self.factom_cli_create.add_fee_to_transaction_input(transaction_name, self.first_address, flag_list=factom_flags_list)

        self.factom_cli_create.sign_transaction(transaction_name)
        self.assertIn(transaction_name, self.factom_cli_create.list_local_transactions(), 'Transaction was created')
        text = self.factom_cli_create.send_transaction(transaction_name)
        chain_dict = self.factom_chain_object.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address)
        entry_credit_amount = int(round(FACTOID_AMOUNT / float(self.ecrate)))
        self.assertEqual(int(balance_after), int(balance_before) + entry_credit_amount, 'Wrong output of transaction')

    def test_create_transaction_with_input_to_output_and_ec(self):
        FACTOID_INPUT_AMOUNT = 2
        FACTOID_OUTPUT_AMOUNT = 1
        ENTRY_CREDIT_AMOUNT = 1
        transaction_name = create_random_string(5)
        self.factom_cli_create.create_new_transaction(transaction_name)
        self.factom_cli_create.add_factoid_input_to_transaction(transaction_name, self.first_address,
                                                                str(FACTOID_INPUT_AMOUNT))
        self.factom_cli_create.add_factoid_output_to_transaction(transaction_name, self.second_address, str(FACTOID_OUTPUT_AMOUNT))

        # check add_entry_credit_output_to_transaction quiet flag
        factom_flags_list = ['-q']
        self.factom_cli_create.add_entry_credit_output_to_transaction(transaction_name, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        self.assertNotIn("Inputs and outputs don't add up", self.factom_cli_create.subtract_fee_from_transaction_output(transaction_name, self.second_address),
            "Entry credit output not added")

        self.factom_cli_create.sign_transaction(transaction_name)

        # check list_local_transactions Names flag
        factom_flags_list = ['-N']
        self.assertIn(transaction_name, self.factom_cli_create.list_local_transactions(flag_list=factom_flags_list), 'Transaction was not created locally in wallet')

        balance_before = int(self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address))
        text = self.factom_cli_create.send_transaction(transaction_name)
        chain_dict = self.factom_chain_object.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = int(self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address))
        balance_expected = int(round(int(balance_before) + ENTRY_CREDIT_AMOUNT / float(self.ecrate)))
        self.assertEqual(balance_after, balance_expected, 'Wrong output of transaction')

    def test_force_buy_entry_credits(self):
        ENTRY_CREDIT_AMOUNT = 150
        balance_before = self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address)
        factom_flags_list = ['-f']
        text = self.factom_cli_create.buy_ec(self.first_address, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        chain_dict = self.factom_chain_object.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address)
        self. assertEqual(int(balance_after), int(balance_before) + ENTRY_CREDIT_AMOUNT, 'Entry credits were not bought')

    def test_quiet_buy_entry_credits(self):
        ENTRY_CREDIT_AMOUNT = 150
        balance_before = self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address)
        factom_flags_list = ['-q']
        self.factom_cli_create.buy_ec(self.first_address, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        balance_after = self.factom_cli_create.check_wallet_address_balance(self.entry_credit_address)
        self. assertEqual(int(balance_after), int(balance_before) + ENTRY_CREDIT_AMOUNT, 'Entry credits were not bought')

    def test_buy_entry_credits_return_tx_id(self):
        ENTRY_CREDIT_AMOUNT = 150
        factom_flags_list = ['-T']
        tx_id = self.factom_cli_create.buy_ec(self.first_address, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        wait_for_ack(tx_id)
        self.assertNotIn('Internal error', self.factom_cli_create.list_transaction (tx_id), 'Transaction not '
                                                                                                    'found')

    def test_force_buy_entry_credits_with_wrong_accounts(self):
        ENTRY_CREDIT_AMOUNT = 150
        factom_flags_list = ['-f']
        self.assertIn('not a Factoid', self.factom_cli_create.buy_ec('wrong_address', self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list))
        self.assertIn('not an Entry', self.factom_cli_create.buy_ec(self.first_address, 'wrong_address', str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list))

    def test_send_factoids(self):
        FACTOID_AMOUNT = 1
        balance_before = self.factom_cli_create.check_wallet_address_balance(self.second_address)
        text = self.factom_cli_create.send_factoids(self.first_address, self.second_address, str(FACTOID_AMOUNT))
        chain_dict = self.factom_chain_object.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.factom_cli_create.check_wallet_address_balance(self.second_address)
        self.assertEqual(int(balance_after), int(balance_before) + FACTOID_AMOUNT)

    def test_for_sof_425(self):
        # rounding error may cause internal error when amount sent is very close to available balance
        second_address = self.factom_cli_create.create_new_factoid_address()
        third_address = self.factom_cli_create.create_new_factoid_address()
        text = self.factom_cli_create.send_factoids(self.first_address, second_address, '100')
        chain_dict = self.factom_chain_object.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)

        self.assertIn('100', self.factom_cli_create.check_wallet_address_balance(second_address), '100 factoids sent did not arrive')
        self.assertIn('balance is too low', self.factom_cli_create.send_factoids(second_address, third_address, '99.9999'), 'Factoids sent when balance insufficient')
        self.assertEqual('0', self.factom_cli_create.check_wallet_address_balance(third_address), 'Factoids sent when balance insufficient')
        self.factom_cli_create.send_factoids(second_address, third_address, '99.99988')
        self.assertEqual('99.99988', self.factom_cli_create.check_wallet_address_balance(third_address), 'Factoids not sent when balance sufficient')
