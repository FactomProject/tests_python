import unittest, json, binascii, hashlib, re, time, sys

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack

@attr(fast=True)
class CLITestsRegression(unittest.TestCase):
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    api_factomd = APIObjectsFactomd()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('shared_test_data.json')

    def setUp(self):
        imported_addresses = self.cli_create.import_addresses(self.data['factoid_wallet_address'], self.data['ec_wallet_address'])
        self.first_address = imported_addresses[0]
        self.entry_credit_address = imported_addresses[1]
        self.second_address = self.cli_create.create_new_factoid_address()
        words = '"'+self.data['words']+'"'
        self.third_address = self.cli_create.import_words_from_koinify_into_wallet(words)
        self.ecrate = self.cli_create.get_entry_credit_rate()

    def test_raw_blocks(self):

        # find a directory block with entries
        block_height = 0
        head_height = int(self.cli_chain.get_directory_block_height_from_head())
        for x in range(0, head_height):
            dblock = json.loads(self.cli_chain.get_directory_block_by_height(x))
            entries = len(dblock['dblock']['dbentries'])
            if entries > 3:
                block_height = x
                break
        self.assertNotEquals(block_height, 0, 'Network has no identities')

        # directory block raw data
        dhash=dblock['dblock']['dbhash']
        self.assertEquals(dblock['rawdata'], self.cli_create.get_raw(dhash), 'Incorrect raw data fetched for Directory Block at height ' + str(block_height))

        # entry block raw data
        # ENTRY = 3 skips over administrative entries
        ENTRY = 3
        keyMR = dblock['dblock']['dbentries'][ENTRY]['keymr']
        eblock = self.cli_chain.get_entry_block(keyMR)
        self.assertIn(self.cli_chain.parse_block_data(eblock)['EBEntry'][0]['EntryHash'], self.cli_create.get_raw(keyMR), 'Incorrect raw data fetched for Entry Block at height ' + str(block_height))

        # admin block raw data
        ablock=json.loads(self.cli_chain.get_admin_block_by_height(block_height))
        ahash=ablock['ablock']['backreferencehash']
        self.assertEquals(ablock['rawdata'], self.cli_create.get_raw(ahash), 'Incorrect raw data fetched for Admin Block at height ' + str(block_height))

        # entry credit block raw data
        ecblock=json.loads(self.cli_chain.get_entrycredit_block_by_height(block_height))
        echash=ecblock['ecblock']['fullhash']
        self.assertEquals(ecblock['rawdata'], self.cli_create.get_raw(echash), 'Incorrect raw data fetched for Entry Credit Block at height ' + str(block_height))

        # factoid block raw data
        fblock=json.loads(self.cli_chain.get_factoid_block_by_height(block_height))
        fhash=fblock['fblock']['keymr']
        self.assertEquals(fblock['rawdata'], self.cli_create.get_raw(fhash), 'Incorrect raw data fetched for Factoid Block at height ' + str(block_height))

    def test_raw_transaction(self):
        FACTOID_AMOUNT = 1
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, str(FACTOID_AMOUNT))
        self.cli_create.add_output_to_transaction(transaction_name,
                                                  self.second_address, str(FACTOID_AMOUNT))
        self.cli_create.add_fee_to_transaction_input(transaction_name, self.first_address)
        self.cli_create.sign_transaction(transaction_name)
        text = self.cli_create.send_transaction(transaction_name)
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']

        wait_for_ack(tx_id)

        raw = self.cli_create.get_raw(tx_id)

        # exclude signatures (164 length for 1 input, 1 output, 0 ecoutputs)
        raw_trimmed = raw[:164]

        # check for non-hex error message
        self.assertTrue(re.search(r'^[0-9a-f]+$', raw_trimmed) is not None, 'Raw data string ' + raw_trimmed + ' is not all hex digits')

        # convert to binary
        serialized_raw_trimmed = binascii.unhexlify(raw_trimmed)

        # hash
        raw_tx_id = hashlib.sha256(serialized_raw_trimmed).hexdigest()

        self.assertEqual(raw_tx_id, tx_id, 'Raw data string is not correct')

    def test_allocate_funds_to_factoid_wallet_address_quiet_output(self):
        AMOUNT_SENT = 1
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, str(AMOUNT_SENT))

        # test add_output_to_transaction_quiet_flag
        factom_flags_list = ['-q']
        self.cli_create.add_output_to_transaction(transaction_name, self.second_address, str(AMOUNT_SENT), flag_list=factom_flags_list)

        # check that output was added
        text = self.cli_create.subtract_fee_from_transaction_output(transaction_name, self.second_address)
        transaction_dict = self.cli_chain.parse_transaction_data(text)
        self.assertEqual(str(AMOUNT_SENT - float(self.ecrate) * 12), transaction_dict['TotalOutputs'], "Quiet output not accepted")
        self.cli_create.sign_transaction(transaction_name)

        # compose transaction
        self.assertTrue('curl' and 'transaction' in self.cli_create.compose_transaction(transaction_name), "Curl command not created")

        # send transaction
        text = self.cli_create.send_transaction(transaction_name)
        transaction_dict = self.cli_chain.parse_transaction_data(text)
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']

        # check for pending transaction
        for x in range(0, self.blocktime+1):
            pending = self.cli_chain.get_pending_transactions()
            if (pending and not pending.isspace()): break
            else: time.sleep(1)
        self.assertLess(x, self.blocktime, 'Transaction never pending')
        self.assertIn(transaction_dict['TxID'], pending, 'Transaction ' + transaction_dict['TxID'] + ' not displayed in pending transactions')

        wait_for_ack(tx_id)

        self.assertNotEqual(self.cli_create.check_wallet_address_balance(self.second_address), '0', 'Factoids were not sent to address: ' + self.second_address)

    def test_if_you_can_compose_wrong_transaction(self):
        self.assertIn("Transaction name was not found", self.cli_create.compose_transaction('not_existing_trans'), 'Non-existent transaction was found in wallet')

    def test_request_balance_wrong_account(self):
        self.assertIn('Undefined or invalid address', self.cli_create.check_wallet_address_balance(
            'Non-existent address'),'Non-existent address is showing up')

    def test_entry_credits_wallet(self):
        self.assertIn(self.entry_credit_address, self.cli_create.export_addresses(), 'Not all addresses were exported')
        self.cli_create.list_addresses()
        self.assertIn(self.entry_credit_address, self.cli_create.list_addresses(), 'Not all addresses were listed')

    def test_create_transaction_with_no_inputs_outputs_or_entry_creds(self):
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.assertIn('Insufficient Fee', self.cli_create.sign_transaction(transaction_name))
        self.assertIn('Cannot send unsigned transaction', self.cli_create.send_transaction(transaction_name))

    def test_delete_transaction(self):
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '1')
        self.cli_create.add_output_to_transaction(transaction_name, self.second_address, '1')
        self.cli_create.subtract_fee_from_transaction_output(transaction_name, self.second_address)
        self.assertIn(transaction_name, self.cli_create.list_local_transactions(), 'Transaction was created')
        self.cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertNotIn(transaction_name, self.cli_create.list_local_transactions(), 'Transaction was not deleted')

    def test_create_transaction_with_not_equal_input_and_output(self):
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '1')
        self.assertIn("Inputs and outputs don't add up",
                      self.cli_create.subtract_fee_from_transaction_output(transaction_name, self.first_address), "Input and output don't add up, but error is not displayed")
        self.cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertNotIn(transaction_name, self.cli_create.list_local_transactions(),
                         'Transaction was not deleted')

    def test_add_input_larger_than_10x_fee_to_correct_transaction_quiet_input(self):
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)

        # test add_input_to_transaction_quiet_flag
        factom_flags_list = ['-q']
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '1', flag_list=factom_flags_list)

        # check that input was added
        text = self.cli_create.add_output_to_transaction(transaction_name, self.first_address,
                                                         '1')
        dict = self.cli_chain.parse_transaction_data(text)
        self.assertEqual('1', dict['TotalInputs'], "Quiet input not accepted")

        self.cli_create.subtract_fee_from_transaction_output(transaction_name, self.first_address)

        # try to overpay
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '10')
        self.assertIn('Overpaying fee', self.cli_create.sign_transaction(transaction_name),
                      'Was able to overpay fee')
        self.cli_create.remove_transaction_from_wallet(transaction_name)
        self.assertNotIn(transaction_name, self.cli_create.list_local_transactions(),
                         'Transaction was not removed')

    def test_create_transaction_with_no_output_or_ec(self):
        balance_before = self.cli_create.check_wallet_address_balance(self.first_address)
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, '1')

        # new input from same address should overwrite 1st input
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, str(format(float(self.ecrate) * 8, 'f')))

        self.cli_create.sign_transaction(transaction_name)
        self.assertIn(transaction_name, self.cli_create.list_local_transactions(), 'Transaction was created')
        text = self.cli_create.send_transaction(transaction_name)
        transaction_dict = self.cli_chain.parse_transaction_data(text)

        # TODO reinstate or otherwise deal with this test when AUT-217 is implemented
        # check for pending transaction return transaction id
        # factom_flags_list = ['-T']
        # for x in range(0, self.blocktime+1):
        #     pending = self.cli_chain.get_pending_transactions(flag_list=factom_flags_list)
        #     if (pending and not pending.isspace()): break
        #     else: time.sleep(1)
        # self.assertLess(x, self.blocktime, 'Transaction never pending')
        # self.assertIn(transaction_dict['TxID'], pending, 'Transaction ' + transaction_dict['TxID'] + ' not displayed in pending transactions')

        balance_after = self.cli_create.check_wallet_address_balance(self.first_address)
        self.assertTrue(abs(float(balance_after) - (float(balance_before) - float(self.ecrate) * 8)) <= 0.0000001, 'Balance is not subtracted correctly')

    def test_create_transaction_with_input_to_ec_quiet_addfee(self):
        FACTOID_AMOUNT = 1

        balance_before = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address, str(FACTOID_AMOUNT))
        self.cli_create.add_entry_credit_output_to_transaction(transaction_name,                 self.entry_credit_address, str(FACTOID_AMOUNT))

        # test add_fee_to_transaction quiet flag
        factom_flags_list = ['-q']
        self.cli_create.add_fee_to_transaction_input(transaction_name, self.first_address, flag_list=factom_flags_list)

        self.cli_create.sign_transaction(transaction_name)
        self.assertIn(transaction_name, self.cli_create.list_local_transactions(), 'Transaction was created')
        text = self.cli_create.send_transaction(transaction_name)
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        entry_credit_amount = int(round(FACTOID_AMOUNT / float(self.ecrate)))
        self.assertEqual(int(balance_after), int(balance_before) + entry_credit_amount, 'Wrong output of transaction')

    def test_create_transaction_with_input_to_output_and_ec(self):
        FACTOID_INPUT_AMOUNT = 2
        FACTOID_OUTPUT_AMOUNT = 1
        ENTRY_CREDIT_AMOUNT = 1
        transaction_name = create_random_string(5)
        self.cli_create.create_new_transaction(transaction_name)
        self.cli_create.add_input_to_transaction(transaction_name, self.first_address,
                                                 str(FACTOID_INPUT_AMOUNT))
        self.cli_create.add_output_to_transaction(transaction_name, self.second_address, str(FACTOID_OUTPUT_AMOUNT))

        # check add_entry_credit_output_to_transaction quiet flag
        factom_flags_list = ['-q']
        self.cli_create.add_entry_credit_output_to_transaction(transaction_name, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        self.assertNotIn("Inputs and outputs don't add up", self.cli_create.subtract_fee_from_transaction_output(transaction_name, self.second_address),
                         "Entry credit output not added")

        self.cli_create.sign_transaction(transaction_name)

        # check list_local_transactions Names flag
        factom_flags_list = ['-N']
        self.assertIn(transaction_name, self.cli_create.list_local_transactions(flag_list=factom_flags_list), 'Transaction was not created locally in wallet')

        balance_before = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        text = self.cli_create.send_transaction(transaction_name)
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        balance_expected = int(round(int(balance_before) + ENTRY_CREDIT_AMOUNT / float(self.ecrate)))
        self.assertEqual(int(balance_after), int(balance_expected), 'Wrong output of transaction')

    def test_force_buy_entry_credits(self):
        ENTRY_CREDIT_AMOUNT = 150
        balance_before = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        factom_flags_list = ['-f']
        text = self.cli_create.buy_entry_credits(self.first_address, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        self. assertEqual(int(balance_after), int(balance_before) + ENTRY_CREDIT_AMOUNT, 'Entry credits were not bought')

    def test_quiet_buy_entry_credits(self):
        ENTRY_CREDIT_AMOUNT = 150
        balance_before = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        factom_flags_list = ['-q']
        self.cli_create.buy_entry_credits(self.first_address, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        balance_after = self.cli_create.check_wallet_address_balance(self.entry_credit_address)
        self. assertEqual(int(balance_after), int(balance_before) + ENTRY_CREDIT_AMOUNT, 'Entry credits were not bought')

    def test_buy_entry_credits_return_tx_id(self):
        ENTRY_CREDIT_AMOUNT = 150
        factom_flags_list = ['-T']
        tx_id = self.cli_create.buy_entry_credits(self.first_address, self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list)
        wait_for_ack(tx_id)
        self.assertNotIn('Internal error', self.cli_create.list_transaction (tx_id), 'Transaction not found')

    def test_force_buy_entry_credits_with_wrong_accounts(self):
        ENTRY_CREDIT_AMOUNT = 150
        factom_flags_list = ['-f']
        self.assertIn('not a Factoid', self.cli_create.buy_entry_credits('wrong_address', self.entry_credit_address, str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list))
        self.assertIn('not an Entry', self.cli_create.buy_entry_credits(self.first_address, 'wrong_address', str(ENTRY_CREDIT_AMOUNT), flag_list=factom_flags_list))

    def test_send_factoids(self):
        FACTOID_AMOUNT = 1
        balance_before = self.cli_create.check_wallet_address_balance(self.second_address)
        text = self.cli_create.send_factoids(self.first_address, self.second_address, str(FACTOID_AMOUNT))
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
        balance_after = self.cli_create.check_wallet_address_balance(self.second_address)
        self.assertEqual(int(balance_after), int(balance_before) + FACTOID_AMOUNT)

    def test_for_sof_425(self):
        # rounding error may cause internal error when amount sent is very close to available balance
        second_address = self.cli_create.create_new_factoid_address()
        third_address = self.cli_create.create_new_factoid_address()
        text = self.cli_create.send_factoids(self.first_address, second_address, '100')
        chain_dict = self.cli_chain.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)

        self.assertIn('100', self.cli_create.check_wallet_address_balance(second_address), '100 factoids sent did not arrive')
        self.assertIn('balance is too low', self.cli_create.send_factoids(second_address, third_address, '99.9999'), 'Factoids sent when balance insufficient')
        self.assertEqual('0', self.cli_create.check_wallet_address_balance(third_address), 'Factoids sent when balance insufficient')
        self.cli_create.send_factoids(second_address, third_address, '99.99988')
        self.assertEqual('99.99988', self.cli_create.check_wallet_address_balance(third_address), 'Factoids not sent when balance sufficient')
