import json

from helpers.factom_cli_methods import send_command_to_cli_and_receive_text

class FactomCliCreate():

    factom_cli_command = 'factom-cli ' #TODO get it globalized
    factom_importaddress = "importaddress "
    factom_newfctaddress = "newfctaddress "
    factom_importwords = "importwords "
    factom_balance = "balance "
    factom_ecrate = "ecrate"
    factom_newtx = "newtx "
    factom_add_transaction_f_input = "addtxinput "
    factom_add_transaction_f_output = "addtxoutput "
    factomd_substract_fee_on_tx = "subtxfee "
    factom_sign_transaction = 'signtx '
    factom_composetx = 'composetx '
    factom_ack = "ack "
    factom_sendtx = "sendtx "
    factom_new_entry_address = "newecaddress"

    def import_address_from_factoid(self, address_to_import_from):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_importaddress,
                                                            address_to_import_from)))

    def create_new_factoid_address(self):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_newfctaddress)))

    def import_words_from_koinify_into_wallet(self, words):
        '''
        Import 12 words from Koinify sale into the Wallet
        :param words: space sepparated 12 words from koinify
        :return: txt, factoid wallet address
        '''
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_importwords, words)))

    def check_waller_address_balance(self, address):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_balance, address)))

    def get_factom_change_entry_credit_conversion_rate(self):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_ecrate)))

    def create_new_transaction_in_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_newtx, transaction_name)))

    def add_foactoid_input_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command,
                                                             self.factom_add_transaction_f_input, transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def add_foactoid_output_to_transaction_in_wallet(self, transaction_name, wallet_address, amount):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command,
                                                             self.factom_add_transaction_f_output, transaction_name,
                                                             ' ', wallet_address, ' ', amount)))

    def set_account_to_substract_fee_from_that_transaction(self, transaction_name, wallet_address):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factomd_substract_fee_on_tx, transaction_name, ' ', wallet_address)))

    def sign_transaction_in_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text((''.join((self.factom_cli_command, self.factom_sign_transaction, transaction_name))))

    def compose_transactsion_and_return_transactoin_code(self, transaction_name):
        transaction = json.loads(send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_composetx, transaction_name))))
        return transaction['params']['transaction']

    def compose_transactsion(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_composetx, transaction_name)))


    def request_transaction_acknowledgement(self, transaction_hash):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_ack, transaction_hash)))


    def send_transaction_and_recive_transaction_id(self, transaction_name):
        transacton = send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_sendtx, transaction_name)))
        return transacton.split(' ')[1]

    def create_entry_credit_address(self):
        return send_command_to_cli_and_receive_text(''.join((self.factom_cli_command, self.factom_new_entry_address)))

