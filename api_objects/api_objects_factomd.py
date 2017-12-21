import requests
import json

from helpers.helpers import read_data_from_json

class APIObjectsFactomd():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://'+self.factomd_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text, r.status_code

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text

    def change_factomd_address(self,change_factomd_address):
        self.factomd_address = change_factomd_address

    def get_directory_block_head(self):
        '''
        Get directory block head
        :return: keymr of head
        '''
        blocks = json.loads(self.send_get_request_with_method('directory-block-head'))
        return blocks["result"]["keymr"]

    def get_directory_block_by_keymr(self, keymr):
        """
        Get directory block
        :param keymr: key mr of block
        :return: list of dicts with entries
        """
        blocks = json.loads(self.send_get_request_with_params_dict('directory-block', {'keymr': keymr})[0])
        return blocks["result"]

    def get_heights(self):
        '''
        Get heights
        :return: list of dicts with heights
        '''
        blocks = json.loads(self.send_get_request_with_method('heights'))
        return blocks['result']

    def get_raw_data_by_hash(self, hash):
        '''
        get raw data
        :param hash: str - hash
        :return: str - data
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('raw-data', {'hash': hash}))
        return blocks['result']['data']

    def get_directory_block_by_height(self, height):
        '''
        Get directory block by height
        :param height: int - height
        :return: dblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('dblock-by-height', {'height': height})[0])
        return blocks['result']['dblock']

    def get_admin_block_by_height(self, height):
        '''
        Get admin block by height
        :param height: int - height
        :return: dblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('ablock-by-height', {'height': height})[0])

        return blocks['result']['ablock']

    def get_entry_credit_block_by_height(self, height):
        '''
        Get entry credit block by height
        :param height: int - height
        :return: ecblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('ecblock-by-height', {'height': height})[0])
        return blocks['result']['ecblock']

    def get_factoid_block_by_height(self, height):
        '''
        Get factoid block by height
        :param height: int - height
        :return: fblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('fblock-by-height', {'height': height})[0])
        return blocks['result']['fblock']

    def get_receipt(self, hash):
        '''
        Get receipt by hash
        :param hash: str, entry hash of transaction
        :return return_data: if API call succeeds, transaction JSON block containing:
            receipt
                entry
                    entryhash
                merklebranch - collection of (left, right, top) triplets which describe the merkletree verifying the receipt of the entry in the factom blockchain.
                    The 1st (bottom of the tree) left entry  will match the entryhash.
                    The 1st right entry will be the minute number of the entry.
                entryblockkeymr
                directoryblockkeymr
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        block = json.loads(self.send_get_request_with_params_dict('receipt', {'hash': hash})[0])
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

    def get_entry_block(self, key_mr):
        '''
        Get entry block by key_mr
        :param key_mr: str - keymr
        :return: header, entrylist
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entry-block', {'KeyMR': key_mr})[0])
        return blocks['result']

    def get_entry_by_hash(self, hash):
        '''
        Get entry by entry hash
        :param hash:
        :return: chainid, content, extids
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entry', {'hash': hash})[0])
        return blocks['result']

    def get_pending_entries(self):
        '''
        Gets pending entries
        :return: JSON with
           entryhash
           chainid
           status
        '''
        blocks = json.loads(self.send_get_request_with_method('pending-entries'))
        return blocks['result']

    def get_transaction_by_hash(self, hash):
        '''
        Gets transaction by transaction hash
        :param hash: str - entryhash
        :return: blocks['result']['factoidtransaction']: JSON block with
           factoidtransaction
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('transaction', {'hash': hash})[0])
        return blocks['result']

    def get_pending_transactions(self, *address):
        '''
        Gets pending transactions
        :param address: str,  optional wallet address
        :return blocks['result']: JSON block - for each pending transaction
           transactionid: str
           status: str, status of the transaction (see status types below)
           inputs - for each input to the transaction
              amount: int, (in factoshis)
              address: str, non-human readable form of the input address
              useraddress: str, public key of the input address
           outputs - for each output of the transaction
              amount: int, (in factoshis)
              address: str, non-human readable form of the output address
              useraddress: str, public key of the output address
           ecoutputs - for each entry credit output of the transaction
              amount: int, (in factoshis)
              address: str, non-human readable form of the entry credit output address
              useraddress: str, public key of the entry credit output address
           fees: int, (in factoshis)

        status types:
        Unknown : not found anywhere
        NotConfirmed : found on local node, but not in network (holding map)
        TransactionACK : found in network, but not written to the blockchain yet (processList)
        DBlockConfirmed : found in blockchain
        '''

        if address:
            blocks = json.loads(
                self.send_get_request_with_params_dict('pending-transactions', {'address': address[0]})[0])
        else:
            blocks = json.loads(self.send_get_request_with_method('pending-transactions'))

        return blocks['result']

    def get_chain_head_by_chain_id(self, chain_id):
        '''
        Gets chain head by chain id
        :param chain_id: str chain id
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('chain-head', {'ChainID': chain_id})[0])
        return blocks['result']['chainhead']

    def get_entry_credit_balance(self, ec_address):
        '''
        Gets entry credit balance by ec address
        :param ec_address: str - ec address
        :return: int - balance
        '''
        block = json.loads(self.send_get_request_with_params_dict('entry-credit-balance', {'address': ec_address})[0])
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']
            error_message = ''
        print 'address', ec_address
        print 'return_data', return_data
        return return_data, error_message

    def get_factoid_balance(self, factoid_address):
        '''
        Gets factoid balance by factoid address
        :param factoid_address: str, address of which to return balance
        :return return_data: if API call succeeds, transaction JSON block containing:
            balance
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        block = json.loads(self.send_get_request_with_params_dict('factoid-balance', {'address': factoid_address})[0])
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']
            error_message = ''
        print 'address', factoid_address
        print 'return_data', return_data
        return return_data, error_message

    def get_entry_credit_rate(self):
        '''
        Gets entry credit rate
        :return return_data: if API call succeeds, JSON block, containing
            rate
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        block = json.loads(self.send_get_request_with_method('entry-credit-rate'))
        print 'block', block
        if 'error' in block:
            return_data = block['error']
            if 'data' in block['error']:
                error_message = block['error']['data']
            else:
                error_message = block['error']['message']
        else:
            return_data = block['result']
            error_message = ''
        print 'ecr return_data', return_data
        return return_data, error_message

    def get_factomd_properties(self):
        '''
        Get factomd properties
        :return blocks['result']: JSON block, containing
           factomdversion: str, current version of the factomd software
           factomapiversion: str, current version of the factomd API software
        '''
        blocks = json.loads(self.send_get_request_with_method('properties'))
        return blocks['result']

    def submit_factoid_by_transaction(self, transaction):
        '''
        Submit factoid
        :param transaction: str, transaction hash
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factoid-submit', {'transaction':
                                                                                             transaction})[0])
        return blocks['result']

    def commit_chain(self, message):
        '''
        Commit chain by message
        :param message: str, the message portion of the API call
        :return return_data: if API call succeeds, transaction JSON block containing:
            message:"Chain Commit Success"
            txid
            entryhash
            chainidhash
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
        '''
        block = json.loads(self.send_get_request_with_params_dict('commit-chain', {'message': message})[0])
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

    def reveal_chain(self, entry):
        '''
        Reveal chain by entry
        :param entry: str, the entry portion of the API call
        :return: return_data: if API call succeeds, reveal JSON block containing:
            message :"Entry Reveal Success"
            entryhash
            chainid
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
      '''
        block = json.loads(self.send_get_request_with_params_dict('reveal-chain', {'entry': entry})[0])
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

    def commit_entry(self, entry):
        '''
        Reveal entry by entry
        :param entry: str, entry generated by compose
        :return blocks['result'] or blocks['error']: JSON, either the result JSON or the error JSON returned by the commit depending on whether or not the commit succeeded
        :return error: boolean, True if the commit failed, False if the commit succeeded
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('reveal-entry', {'entry': entry})[0])
        if 'error' in blocks:
            error = True
            return blocks['error'], error
        else:
            error = False
            return blocks['result'], error

    def reveal_entry(self, entry):
        '''
        Reveal entry by entry
        :param entry: str, entry generated by compose
        :return blocks['result'] or blocks['error']: JSON, either the result JSON or the error JSON returned by the commit depending on whether or not the commit succeeded
        :return error: boolean, True if the commit failed, False if the commit succeeded
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('reveal-entry', {'entry': entry}))
        return blocks['result']

    def get_status(self, hash_or_tx_id, chain_id):
        '''
        This api call is used to find the status of a transaction, whether it be a factoid, reveal entry, or commit entry.
        chainid for factoid transaction is always 000...f, abbreviated to just f
        :return:
        Status types
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('ack', {'hash': hash_or_tx_id, 'chainid': chain_id})[0])
        return blocks["result"]

    def send_raw_message(self, message):
        '''
        Send raw message
        :param message: str, pure message to be injected into system
        :return: return_data: if API call succeeds, JSON block containing:
            message :"Successfully sent the message"
        if API call fails, error JSON block containing:
            code
            message
            data (optional)
        :return error_message: if API call succeeds, nil
        if API call fails, useful error message
      '''
        block = json.loads(self.send_get_request_with_params_dict('send-raw-message', {'message': message})[0])
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

    def get_current_minute(self):
        '''
        Get current minute of the directory block
        :return: current minute currentblocktime
        '''
        blocks = json.loads(self.send_get_request_with_method('current-minute'))
        return blocks['result']

    def get_factoid_block_by_keymr(self, keymr):
        '''
        Get factoid block by keymr
        :param keymr: keymr
        :return: fblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factoid-block', {'KeyMR': keymr})[0])
        return blocks['result']['fblock']

    def get_entrycredit_block_by_keymr(self, keymr):
        '''
        Get factoid block by keymr
        :param keymr: keymr
        :return: ecblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entrycredit-block', {'KeyMR': keymr})[0])
        return blocks['result']['ecblock']


    def get_admin_block_by_keymr(self, keymr):
        '''
        Get factoid block by keymr
        :param keymr: keymr
        :return: ablock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('admin-block', {'KeyMR': keymr})[0])
        return blocks['result']['ablock']
