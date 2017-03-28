from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject
from helpers.helpers import read_data_from_json

class FactomCliCreate(FactomBaseObject):
    data = read_data_from_json('shared_test_data.json')
    _factom_importaddress = "importaddress "
    _factom_newfctaddress = "newfctaddress "
    _factom_importwords = "importkoinify "
    _factom_balance = "balance "
    _factom_ecrate = "ecrate"
    _factom_newtx = "newtx "
    _factom_add_transaction_f_input = "addtxinput "
    _factom_add_transaction_f_output = "addtxoutput "
    _factom_add_transaction_ec_output = "addtxecoutput "
    _factomd_subtract_fee_on_tx = "subtxfee "
    _factomd_add_fee_on_tx = "addtxfee "
    _factom_sign_transaction = 'signtx '
    _factom_composetx = 'composetx '
    _factom_ack = "status "
    _factom_sendtx = "sendtx "
    _factom_new_entry_address = "newecaddress"
    _factom_listadresses = "listaddresses"
    _factom_exportadresses = "exportadresses"
    _factom_list_tx_id = "listtxs id"
    _factom_list_local_txs = "listtxs tmp"
    _factom_remove_tx = "rmtx "
    _factom_buy_ec = "buyec "
    _factom_send_factoids = "sendfct "
    _factom_wallet_backup_wallet = "backupwallet"

    def import_address_from_factoid(self, address_to_import_from):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_importaddress,
                                                             address_to_import_from)))

    def create_new_factoid_address(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_newfctaddress)))

    def import_words_from_koinify_into_wallet(self, words):
        '''
        Import 12 words from Koinify sale into the Wallet
        :param words: space sepparated 12 words from koinify
        :return: txt, factoid wallet address
        '''
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_importwords, words)))

    def check_wallet_address_balance(self, address):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_balance, address)))

    def check_wallet_address_balance_remote(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_balance,
                                                                   '-r ',
                                                             self.data['remote_address'])))

    def get_factom_change_entry_credit_conversion_rate(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_ecrate)))

    def create_new_transaction_in_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_newtx, transaction_name)))

    def quiet_create_new_transaction_in_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_newtx, ' -q ', transaction_name)))

    def add_factoid_input_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_f_input, ' -q ', transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def quiet_add_factoid_input_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_f_input, transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def add_factoid_output_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_f_output, transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def quiet_add_factoid_output_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_f_output, transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def add_factoid_output_to_transaction_remote(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_f_output, ' -r ', self.data['remote_address'], ' ', transaction_name, wallet_address, ' ', amount)))

    def add_entry_credit_output_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_ec_output, transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def quiet_add_entry_credit_output_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_transaction_ec_output, ' -q ', transaction_name, ' ', wallet_address, ' ', amount)))

    def add_entry_credit_output_to_transaction_remote(self, transaction_name, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_add_transaction_ec_output, ' -r ', self.data['remote_address'], ' ', transaction_name, amount)))

    def set_account_to_subtract_fee_from_that_transaction(self, transaction_name, wallet_address):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_subtract_fee_on_tx, transaction_name, ' ', wallet_address)))

    def quiet_set_account_to_subtract_fee_from_that_transaction(self, transaction_name, wallet_address):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_subtract_fee_on_tx, ' -q ', transaction_name, ' ', wallet_address)))

    def set_account_to_add_fee_from_transaction_input(self, transaction_name, wallet_address):
        return send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factomd_add_fee_on_tx, transaction_name, ' ', wallet_address)))

    def quiet_set_account_to_add_fee_from_transaction_input(self, transaction_name, wallet_address):
        return send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factomd_add_fee_on_tx, ' -q ', transaction_name, ' ', wallet_address)))

    def sign_transaction_in_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text(
            (''.join((self._factom_cli_command, self._factom_sign_transaction, transaction_name))))

    def quiet_sign_transaction_in_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text((''.join((self._factom_cli_command, self._factom_sign_transaction, ' -q ', transaction_name))))

    def compose_transaction_and_return_transaction_code(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_composetx, transaction_name))).split('"')[11]

    def compose_transaction(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_composetx, transaction_name)))


    def request_transaction_acknowledgement(self, transaction_hash):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_ack, transaction_hash)))

    def send_transaction_and_receive_transaction_id(self, transaction_name):
        transacton = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_sendtx, transaction_name)))
        return transacton.split(' ')[1]

    def send_transaction(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_sendtx, transaction_name)))

    def create_entry_credit_address(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_new_entry_address)))

    def list_addresses(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_listadresses)))

    def export_addresses(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_exportadresses)))

    def list_transaction(self, tx_id):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_list_tx_id, ' ', tx_id)))

    def list_local_transactions(self):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_list_local_txs)))

    def remove_transaction_from_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_remove_tx, transaction_name)))

    def buy_ec(self, wallet_address, ec_wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_buy_ec, ' ', wallet_address, ' ',
                                                             ec_wallet_address, ' ', amount)))

    def buy_ec_return_tx_id(self, wallet_address, ec_wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_buy_ec, ' -T ', wallet_address, ' ',
                                                             ec_wallet_address, ' ', amount)))

    def force_buy_ec(self, wallet_address, ec_wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_buy_ec, '-f ', wallet_address, ' ',
                                                             ec_wallet_address, ' ', amount)))

    def quiet_buy_ec(self, wallet_address, ec_wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_buy_ec, '-q ', wallet_address, ' ',
                                                             ec_wallet_address, ' ', amount)))

    def buy_ec_remote(self, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_buy_ec, ' -r ', wallet_address, ' ', self.data['remote_address'], ' ', amount)))

    def send_factoids(self, wallet_address_one, wallet_address_two, amount):
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_send_factoids, wallet_address_one, ' ',
                                                             wallet_address_two, ' ', amount)))
    def backup_wallet(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command,
                                                             self._factom_wallet_backup_wallet)))
        return text


