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

    def identity_key(self,publickey):
        '''
        retrieve an identity that is already stored in the wallet.
        Input: public key
        Output: public key and secret key
        '''
        block = json.loads(self.send_post_request_with_params_dict('identity-key',{'public': publickey}))
        return block['result']


    def generate_identity_key(self):
        '''
        generate an identity key.
        Input: None
        Output: public key and secret key
        '''
        block = json.loads(self.send_get_request_with_method('generate-identity-key'))
        return block['result']


    def all_identity_keys(self):
        '''
        retrieve all the identities that is already stored in the wallet.
        Input: None
        Output: public key and secret key
        '''
        block = json.loads(self.send_get_request_with_method('all-identity-keys'))

        return block['result']


    def import_identity_keys(self,secretkey):
        '''
        import identities to the wallet
        Input: secret key
        Output: public key and secret key
        '''
        block = json.loads(self.send_post_request_with_params_dict('import-identity-key',{'public': secretkey}))
        return block['result']

    def active_identity_keys(self,chainid,height):
        '''
        This command will return the active public keys for an identity at a given point in time.
        Time is indicated by the block height of the Factom blockchain at the desired time.
        Input: chainid, height
        Output: set of four public keys
        '''
        block = json.loads(self.send_post_request_with_params_dict('active-identity-keys', {'chainid': chainid,'height': height}))
        return block['result']


    def remove_identity_keys(self,secretkey):
        '''
        remove identities from the wallet
        Input: secret key
        Output: successful or not
        '''
        block = json.loads(self.send_post_request_with_params_dict('remove-identity-key',{'public': secretkey}))
        return block['result']


    def compose_identity_chain(self, external_ids, pubkeys, ec_address):
        '''
        https://docs-dev.factom.com/api#compose-identity-chain
        Create both the 'commit-chain' JSON and the 'reveal-chain' JSON that can then be sent in API calls to create a identity chain at a later time
        :param external_ids: list, all the external ids (in hex) that will determine the identity of the chain
        :param pubkey: list of public key\s of the identity
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
        block = json.loads(self.send_post_request_with_params_dict('compose-identity-chain', {'name': external_ids, 'pubkeys': pubkeys, 'ecpub': ec_address}))
        if 'error' in str(block):
            exit('compose entry failed - ' + str(block['error']))
        else: return block['result']


    def compose_identity_key_replacement(self, chainid, oldkey,newkey,signerkey, ec_address,force):
        '''
        https://docs-dev.factom.com/api#compose-identity-key-replacement
        this method is used to replace the identity key
        :param chainid: ID of the identity chain in question
        :param oldkey: The oldkey is the private key for the level to be replaced.
        :param newkey: The new is the key that will be replacing it
        :param signerkey: The signerkey is a private key that must be from the level directly above the oldkey in the Identity Chain.
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
        block = json.loads(self.send_post_request_with_params_dict('compose-identity-key-replacement', {'chainid': chainid, 'oldkey': oldkey, 'newkey': newkey, 'signerkey': signerkey, 'ecpub': ec_address,'force': force}))
        if 'error' in str(block):
            exit('compose entry failed - ' + str(block['error']))
        else: return block['result']



    def compose_identity_attribute(self,receiver_chainid,destination_chainid,attributes, signer_chainid,signerkey,ecpub,force):
        '''
        https://docs-dev.factom.com/api#compose-identity-attribute
        This method helps you endorse an attribute that has already been registered on the Factom blockchain.
        :param receiver-chainid: This is the Chain ID for the identity receiving the endorsement.
        :param destination-chainid: The Chain ID of the destination.
        :param attributes: The attribute you are attesting to.
        :param signer-chainid: he signer-chainid leads to the Identity Chain of the signing party.
        :param signerkey: The signerkey should be the secret key of the lowest level key from the signer's Identity
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
        block = json.loads(self.send_post_request_with_params_dict('compose-identity-attribute', {'receiver-chainid': receiver_chainid, 'destination-chainid': destination_chainid,
                                                                                                  'attributes': attributes,'signerchainid': signer_chainid, 'signerkey': signerkey,'ecpub': ecpub,'force':force}))
        if 'error' in str(block):
            exit('compose entry failed - ' + str(block['error']))
        else: return block['result']


    def compose_identity_attribute_endorsement(self, destination_chainid,entryhash,signerkey,signer_chainid,ecpub,force):
        '''
        https://docs-dev.factom.com/api#compose-identity-attribute
        This method helps you endorse an attribute that has already been registered on the Factom blockchain.
        :param destination-chainid:This is the ID of the identity chain in question.
        :param entryhash: entryhash to be endorsed
        :param signer-chainid: he signer-chainid leads to the Identity Chain of the signing party.
        :param signerkey: The signerkey should be the secret key of the lowest level key from the signer's Identity
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
        block = json.loads(self.send_post_request_with_params_dict('compose-identity-attribute-endorsement', {'destination-chainid': destination_chainid,
                                                                                                  'entryhash': entryhash, 'signerkey': signerkey, 'signerchainid': signer_chainid, 'ecpub': ecpub, 'force': force}))
        if 'error' in str(block):
            exit('compose entry failed - ' + str(block['error']))
        else: return block['result']

