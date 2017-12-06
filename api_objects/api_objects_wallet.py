import requests, json, ast

from helpers.helpers import read_data_from_json

class APIObjectsWallet():

    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']

    def send_post_request_with_params_dict(self, method, params_dict):
        url = 'http://'+ self.wallet_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        return r.text

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://' + self.wallet_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text

    def send_get_request_with_method(self, method):
        url = 'http://' + self.wallet_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text

    def check_address_by_public_address(self, address):
        '''
        Import address by public address
        :param address: str
        :return: secret address
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('address', {'address': address}))
        return blocks["result"]["secret"]

    def check_all_addresses(self):
        '''
        Import all addresses from wallet
        :return: list of dicts, addresses
        '''
        blocks = json.loads(self.send_get_request_with_method('all-addresses'))
        return blocks['result']['addresses']

    def generate_ec_address(self):
        '''
        Generate ec addresses
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_method('generate-ec-address'))
        return blocks['result']['public']

    def generate_factoid_address(self):
        '''
        Generate ec addresses
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_method('generate-factoid-address'))
        return blocks['result']['public']

    def import_addresses(self, *secret_addresses):
        '''
        Imports address by secret address and returns public
        :param *secret_address: list of 1 or more str
        :return: list of corresponding public addresses str
        '''
        result = json.loads(self.send_post_request_with_params_dict('import-addresses', ast.literal_eval(json.dumps({'addresses': [{'secret': address} for address in secret_addresses]}))))
        public=[]
        for i in range(len(secret_addresses)):
            public.append(result['result']['addresses'][i]['public'])
        return public

    def import_mnemonic(self, words):
        '''
        Import from mnemonics
        :param words: string 12 words
        :return: json
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('import-mnemonic', {'words': words}))
        return blocks#["result"]["public"]

    def list_all_transactions_in_factoid_blockchain(self):
        '''
        List all transactions
        :return: json, transactions
        '''
        block = json.loads(self.send_get_request_with_method('transactions'))
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def list_transactions_by_txid(self, txid):
        '''

        :param txid: str
        :return:
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'txid': txid}))
        return blocks["result"]

    def list_transactions_by_address(self, address):
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'address': address}))
        return blocks["result"]

    def list_transactions_by_range(self, start, end):
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'range': {'start': start, "end": end}}))
        return blocks["result"]

    def create_new_transaction(self, transaction_name):
        '''
        Create new transaction
        :param transaction_name: str - name
        :return: transaction
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('new-transaction', {'tx-name': transaction_name}))
        return blocks["result"]

    def list_current_working_transactions_in_wallet(self):
        blocks = self.send_get_request_with_method('tmp-transactions')
        return blocks

    def delete_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('delete-transaction', {'tx-name': transaction_name}))
        return blocks["result"]

    def add_input_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-input', {'tx-name': transaction_name,
        'address':address,'amount': amount}))
        return blocks#["result"]

    def add_output_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-output', {'tx-name': transaction_name,
        'address': address, 'amount': amount}))
        return blocks["result"]

    def add_entry_credit_output_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-ec-output', {'tx-name': transaction_name, 'address': address, 'amount': amount}))
        return blocks["result"]

    def add_fee_to_transaction(self, transaction_name, address):
        blocks = json.loads(self.send_post_request_with_params_dict('add-fee', {'tx-name': transaction_name,
                                                                                 'address': address}))
        return blocks["result"]

    def subtract_fee_from_transaction(self, transaction_name, address):
        blocks = json.loads(self.send_post_request_with_params_dict('sub-fee', {'tx-name': transaction_name,
                                                                               'address': address}))
        return blocks

    def sign_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('sign-transaction', {'tx-name': transaction_name}))
        return blocks

    def compose_chain_old(self, external_ids, content, ecpub):
        blocks = json.loads(self.send_post_request_with_params_dict('compose-chain',
                 {'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ecpub}))
        if 'error' in blocks:
            return_data = blocks['error']
            if 'data' in blocks['error']:
                error_message = blocks['error']['data']
            else:
                error_message = blocks['error']['message']
        else:
            return_data = blocks['result']
            error_message = ''
        return return_data, error_message

    def compose_entry(self, chainid, external_ids, content, ecpub):
        blocks = json.loads(self.send_post_request_with_params_dict('compose-entry',
                 {'entry': {'chainid': chainid, 'extids': external_ids, 'content': content}, 'ecpub': ecpub}))
        if 'error' in blocks:
            return_data = blocks['error']
            if 'data' in blocks['error']:
                error_message = blocks['error']['data']
            else:
                error_message = blocks['error']['message']
        else:
            return_data = blocks['result']
            error_message = ''
        return return_data, error_message

    def compose_chain(self, external_ids, content, ec_address):
        '''
        Create both the 'commit-chain' JSON and the 'reveal-chain' JSON that can then be sent in API calls to create a chain at a later time
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param content: str, the content (in hex) of the 1st entry of the chain
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
        :return return_data: if API call succeeds, JSON of the two API calls (commit and reveal) that when sent later will actually create the chain
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
       '''
        block = json.loads(self.send_post_request_with_params_dict('compose-chain',
                 {'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ec_address}))
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']
            error_message = ''
        return return_data, error_message

    def compose_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('compose-transaction',
                                                                    {'tx-name': transaction_name}))
        return blocks["result"]['params']['transaction']

    def get_wallet_height(self):
        blocks = json.loads(self.send_get_request_with_method('get-height'))
        return blocks["result"]

    def get_wallet_properties(self):
        '''
        Get wallet properties
        :return blocks['result']: JSON block, containing
           walletversion: str, current version of the wallet software
           walletapiversion: str, current version of the wallet API software
        '''
        blocks = json.loads(self.send_get_request_with_method('properties'))
        return blocks['result']

