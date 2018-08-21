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
        Return private address corresponding to public address
        :param address: str
        :return: secret address
        '''
        blocks = json.loads(self.send_post_request_with_params_dict('address', {'address': address}))
        if 'error' in str(blocks): exit('check address failed - ' + str(blocks))
        else: return blocks["result"]["secret"]

    def check_all_addresses(self):
        '''
        Return all public and private addresses
        :return: list of dicts, addresses
        '''
        blocks = json.loads(self.send_get_request_with_method('all-addresses'))
        if 'error' in str(blocks): exit('check all addresses failed - ' + str(blocks))
        else: return blocks['result']['addresses']

    def generate_ec_address(self):
        '''
        Generate ec addresses
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_method('generate-ec-address'))
        if 'error' in str(blocks): exit('generate ec address failed - ' + str(blocks))
        else: return blocks['result']['public']

    def generate_factoid_address(self):
        '''
        Generate ec addresses
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_method('generate-factoid-address'))
        if 'error' in str(blocks): exit('generate factoid address failed - ' + str(blocks))
        else: return blocks['result']['public']

    def import_addresses(self, *secret_addresses):
        '''
        Imports addresses by secret address and returns public addresses
        :param *secret_addresses: list, 1 or more private keys
        :return: list, corresponding public addresses
        '''
        result = json.loads(self.send_post_request_with_params_dict('import-addresses', ast.literal_eval(json.dumps({'addresses': [{'secret': address} for address in secret_addresses]}))))
        if 'error' in str(result): exit('import addresses failed - ' + str(result))
        else:
            public=[]
            for i in range(len(secret_addresses)):
                public.append(result['result']['addresses'][i]['public'])
            return public

    def import_mnemonic(self, words):
        '''
        Import from mnemonics
        :param words: str, 12 words
        :return: str, public key of imported address
        '''
        block = json.loads(self.send_get_request_with_params_dict('import-koinify', {'words': words}))
        if 'error' in str(block): exit('Import 12 words failed - ' + str(block['error']))
        else: return block['result']['public']

    def list_all_transactions_in_factoid_blockchain(self):
        '''
        List all transactions
        :return block['result']['transactions']: list of JSON transactions, each containing:
            txid
            blockheight
            feespaid: factoshis
            signed: boolean
            timestamp
            totalecoutputs: factoshis
            totalinputs: factoshis
            totaloutputs: factoshis
            inputs
                address
                amount: factoshis
            outputs
                address
                amount: factoshis
            ecoutputs
                address
                amount: factoshis
        '''
        block = json.loads(self.send_get_request_with_method('transactions'))
        if 'error' in str(block): exit('transaction list failed - ' + str(block['error']))
        else: return block['result']['transactions']

    def list_transactions_by_txid(self, txid):
        '''
        :param txid: str
        :return: JSON transaction containing:
            txid
            feespaid: factoshis
            signed: boolean
            timestamp
            totalecoutputs: factoshis
            totalinputs: factoshis
            totaloutputs: factoshis
            inputs
                address
                amount: factoshis
            outputs
                address
                amount: factoshis
            ecoutputs
                address
                amount: factoshis
        '''
        block = json.loads(self.send_post_request_with_params_dict('transactions', {'txid': txid}))
        if 'error' in str(block): exit('transaction list by transaction id failed - ' + str(block['error']))
        else: return block['result']['transactions']

    def list_transactions_by_address(self, address):
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'address': address}))
        if 'error' in str(blocks):
            exit('transaction list by address failed - ' + str(blocks['error']))
        else: return blocks["result"]

    def list_transactions_by_range(self, start, end):
        blocks = json.loads(self.send_post_request_with_params_dict('transactions', {'range': {'start': start, "end": end}}))
        if 'error' in str(blocks):
            exit('transaction list by range failed - ' + str(blocks['error']))
        else: return blocks["result"]

    def create_new_transaction(self, transaction_name):
        '''
        Create new transaction
        :param transaction_name: str, name
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
        return blocks["result"]

    def add_output_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-output', {'tx-name': transaction_name,
        'address': address, 'amount': amount}))
        return blocks["result"]

    def add_entry_credit_output_to_transaction(self, transaction_name, address, amount):
        blocks = json.loads(self.send_post_request_with_params_dict('add-ec-output', {'tx-name': transaction_name, 'address': address, 'amount': amount}))
        return blocks["result"]

    def add_fee_to_transaction(self, transaction_name, address):
        blocks = json.loads(self.send_post_request_with_params_dict('add-fee', {'tx-name': transaction_name, 'address': address}))
        return blocks["result"]

    def subtract_fee_from_transaction(self, transaction_name, address):
        blocks = json.loads(self.send_post_request_with_params_dict('sub-fee', {'tx-name': transaction_name, 'address': address}))
        return blocks

    def sign_transaction(self, transaction_name):
        blocks = json.loads(self.send_post_request_with_params_dict('sign-transaction', {'tx-name': transaction_name}))
        return blocks

    def compose_chain(self, external_ids, content, ec_address):
        '''
        Create both the 'commit-chain' JSON and the 'reveal-chain' JSON that can then be sent in API calls to create a chain at a later time
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param content: str, the content (in hex) of the 1st entry of the chain
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the chain
        :return return_data: if API call succeeds, JSON of the two API calls (commit and reveal) that when sent later will actually create the chain
            commit
                jsonrpc:"2.0"
                id
                params
                    message
                method: "commit-chain"
            reveal
                jsonrpc:"2.0"
                id
                params
                    entry
                method: "reveal-chain"
       '''
        block = json.loads(self.send_post_request_with_params_dict('compose-chain',
                 {'chain': {'firstentry': {'extids': external_ids, 'content': content}}, 'ecpub': ec_address}))
        if 'error' in str(block):
            exit('compose entry failed - ' + str(block['error']))
        else: return block['result']

    def compose_entry(self, chainid, external_ids, content, ec_address):
        '''
        Create both the 'commit-entry' JSON and the 'reveal-entry' JSON that can then be sent in API calls to create an entry at a later time
        :param chainid: of chain in which to make the entry
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the entry
        :param content: str, the content (in hex) of the entry
        :param ec_address: str, the public key of the entry credit address that will pay for the creation of the entry
        :return: JSON of the two API calls (commit and reveal) that when sent later will actually create the entry
            commit
                jsonrpc:"2.0"
                id
                params
                    message
                method: "commit-entry"
            reveal
                jsonrpc:"2.0"
                id
                params
                    entry
                method: "reveal-entry"
        '''
        block = json.loads(self.send_post_request_with_params_dict('compose-entry',
                 {'entry': {'chainid': chainid, 'extids': external_ids, 'content': content}, 'ecpub': ec_address}))
        if 'error' in str(block):
            exit('compose entry failed - ' + str(block['error']))
        else:
            return block['result']

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

    def wallet_balances(self):
        '''
        Gets the total balances of acknowledged and saved balances for all addresses in the currently running factomd wallet
        :return: dictionaries of the two kinds of totals (in factoshis) of all factoid addresses in the currently running factomd wallet
            ack
            saved
        :return: dictionaries of the two kinds of totals (in entry credits) of all entry credit addresses in the currently running factomd wallet
            ack
            saved
        '''
        block = json.loads(self.send_get_request_with_method('wallet-balances'))
        return block['result']['fctaccountbalances'], block['result']['ecaccountbalances']

