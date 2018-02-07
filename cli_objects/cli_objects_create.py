from helpers.cli_methods import send_command_to_cli_and_receive_text
from cli_objects_base_ import CLIObjectsBase

class CLIObjectsCreate(CLIObjectsBase):
    _ecrate = "ecrate"
    _buy_entry_credits = "buyec "
    _send_factoids = "sendfct "
    _importwords = "importkoinify "
    _importaddress = "importaddress "
    _export_addresses = "exportaddresses"
    _newfctaddress = "newfctaddress "
    _new_entry_credit_address = "newecaddress"
    _list_addresses = "listaddresses"
    _balance = "balance "
    _newtx = "newtx "
    _add_input_to_transaction = "addtxinput "
    _add_output_to_transaction = "addtxoutput "
    _add_entry_credit_output_to_transaction = "addtxecoutput "
    _subtract_fee_in_transaction = "subtxfee "
    _add_fee_in_transaction = "addtxfee "
    _sign_transaction = 'signtx '
    _send_transaction = "sendtx "
    _compose_transaction = 'composetx '
    _list_transactions = ' listtxs '
    _list_transaction = "listtxs id"
    _list_local_transactions = "listtxs tmp"
    _remove_transaction = "rmtx "
    _acknowledge = "status "
    _backup_wallet = "backupwallet"
    _get_raw = 'get raw '

    def import_addresses(self, *addresses):
        address_string = addresses[0]
        for address in addresses[1:]:
            address_string = address_string + ' ' + address
        result = send_command_to_cli_and_receive_text(''.join((self._cli_command, self._importaddress,
                                                               address_string)))
        result = result.split('\n')
        return result

    def create_new_factoid_address(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._newfctaddress)))

    def import_words_from_koinify_into_wallet(self, words):
        '''Import 12 words from Koinify sale into the Wallet
        :param words: space separated 12 words from koinify
        :return: str, factoid wallet address'''

        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._importwords, words)))

    def check_wallet_address_balance(self, address):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._balance, address)))

    def check_wallet_address_balance_remote(self, address):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._balance, '-r ', address)))

    def get_entry_credit_rate(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._ecrate)))

    def create_new_transaction(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._newtx, transaction_name)))

    def add_input_to_transaction(self, transaction_name, wallet_address, amount, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._add_input_to_transaction, flags, ' ', transaction_name, ' ', wallet_address, ' ', amount)))

    def add_output_to_transaction(self, transaction_name, wallet_address, amount, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._add_output_to_transaction, flags, ' ', transaction_name, ' ', wallet_address, ' ', amount)))

    def subtract_fee_from_transaction_output(self, transaction_name, wallet_address):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._subtract_fee_in_transaction, transaction_name, ' ', wallet_address)))

    def add_fee_to_transaction_input(self, transaction_name, wallet_address, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join(
            (self._cli_command, self._add_fee_in_transaction, flags, ' ', transaction_name, ' ', wallet_address)))

    def sign_transaction(self, transaction_name):
        return send_command_to_cli_and_receive_text((''.join((self._cli_command, self._sign_transaction, transaction_name))))

    def compose_transaction(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._compose_transaction, transaction_name)))

    def request_transaction_acknowledgement(self, transaction_hash):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._acknowledge, transaction_hash)))

    def send_transaction(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._send_transaction, transaction_name)))

    def create_entry_credit_address(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._new_entry_credit_address)))

    def list_addresses(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_addresses)))

    def export_addresses(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._export_addresses)))

    def get_all_transactions(self):
        text = send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_transactions)))
        return text

    def list_transaction(self, tx_id):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_transaction, ' ',
                                                             tx_id)))

    def list_local_transactions(self, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_local_transactions,
                                                             ' ', flags)))

    def remove_transaction_from_wallet(self, transaction_name):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._remove_transaction, transaction_name)))

    def add_entry_credit_output_to_transaction(self, transaction_name, wallet_address, amount, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._add_entry_credit_output_to_transaction, flags, ' ', transaction_name, ' ', wallet_address, ' ', amount)))

    def buy_entry_credits(self, wallet_address, ec_wallet_address, amount, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._buy_entry_credits, flags, ' ', wallet_address, ' ', ec_wallet_address, ' ', amount)))

    def send_factoids(self, address_from, address_to, amount):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._send_factoids, address_from, ' ', address_to, ' ', amount)))

    def backup_wallet(self):
        text = send_command_to_cli_and_receive_text(''.join((self._cli_command,
                                                             self._backup_wallet)))
        return text

    def get_raw(self, hash):
        text = send_command_to_cli_and_receive_text(''.join((self._cli_command, self._get_raw, hash)))
        return text


