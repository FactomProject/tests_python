import requests, json

from helpers.helpers import read_data_from_json

class APIObjectsFactomd():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def send_get_request_with_params_dict(self, method, params_dict, allow_fail=False):
        url = 'http://'+self.factomd_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        if not allow_fail and not r.status_code == requests.codes.ok: exit('Get failed - ' + r.text)
        return r.text

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        print data
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        if not r.status_code == requests.codes.ok: exit('Get failed - ' + r.text)
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
        blocks = json.loads(self.send_get_request_with_params_dict('directory-block', {'keymr': keymr}))
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
        blocks = json.loads(self.send_get_request_with_params_dict('dblock-by-height', {'height': height}))
        return blocks['result']['dblock']

    def get_admin_block_by_height(self, height):
        '''
        Get admin block by height
        :param height: int - height
        :return: dblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('ablock-by-height', {'height': height}))
        return blocks['result']['ablock']

    def get_entry_credit_block_by_height(self, height):
        '''
        Get entry credit block by height
        :param height: int - height
        :return: ecblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('ecblock-by-height', {'height': height}))
        return blocks['result']['ecblock']

    def get_factoid_block_by_height(self, height):
        '''
        Get factoid block by height
        :param height: int - height
        :return: fblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('fblock-by-height', {'height': height}))
        return blocks['result']['fblock']

    def get_receipt(self, hash):
        '''
        Get receipt by hash
        :param hash: str, entry hash of transaction
        :return return_data: transaction JSON block containing:
            receipt
                entry
                    entryhash
                merklebranch - collection of (left, right, top) triplets which describe the merkletree verifying the receipt of the entry in the factom blockchain.
                    The 1st (bottom of the tree) left entry  will match the entryhash.
                    The 1st right entry will be the minute number of the entry.
                entryblockkeymr
                directoryblockkeymr
        '''
        block = json.loads(self.send_get_request_with_params_dict('receipt', {'hash': hash}))
        if 'error' in str(block): exit('Receipt creation for hash ' + hash + ' failed - ' + str(block['error']))
        else: return block['result']

    def get_entry_block(self, key_mr):
        '''
        Get entry block by key_mr
        :param key_mr: str - keymr
        :return: header, entrylist
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entry-block', {'KeyMR': key_mr}))
        return blocks['result']

    def get_entry_by_hash(self, hash):
        '''
        Get entry by entry hash
        :param hash:
        :return: chainid, content, extids
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entry', {'hash': hash}))
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
        blocks = json.loads(self.send_get_request_with_params_dict('transaction', {'hash': hash}))
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
                self.send_get_request_with_params_dict('pending-transactions', {'address': address[0]}))
        else:
            blocks = json.loads(self.send_get_request_with_method('pending-transactions'))

        return blocks['result']

    def get_chain_head_by_chain_id(self, chain_id):
        '''
        Gets chain head by chain id
        :param chain_id: str chain id
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('chain-head', {'ChainID': chain_id}))
        return blocks['result']['chainhead']

    def get_entry_credit_balance(self, ec_address):
        '''
        Gets entry credit balance by ec address
        :param ec_address: str, ec address
        :return: int, balance
        '''
        block = json.loads(self.send_get_request_with_params_dict('entry-credit-balance', {'address': ec_address}))
        if 'error' in str(block): exit('Balance for entry credit address ' + ec_address + ' failed - ' + str(block['error']))
        else: return block['result']['balance']

    def get_factoid_balance(self, factoid_address):
        '''
        Gets factoid balance by factoid address
        :param factoid_address: str, address of which to return balance
        :return: int, balance
        '''
        block = json.loads(self.send_get_request_with_params_dict('factoid-balance', {'address': factoid_address}))
        if 'error' in str(block): exit('Balance for factoid address ' + factoid_address + ' failed - ' + str(block['error']))
        else: return block['result']['balance']

    def get_entry_credit_rate(self):
        '''
        Gets entry credit rate
        :return int, how many factoshis it currently takes to create an entry credit
        '''
        block = json.loads(self.send_get_request_with_method('entry-credit-rate'))
        if 'error' in str(block): exit('Entry_credit_rate failed - ' + str(block['error']))
        else: return block['result']['rate']

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
                                                                                             transaction}))
        return blocks['result']

    def commit_chain(self, message):
        '''
        Commit chain by message
        :param message: str, message generated by compose
        :return: block['result']: transaction JSON block containing:
            message:"Chain Commit Success"
            txid
            entryhash
            chainidhash
        '''
        block = json.loads(self.send_get_request_with_params_dict('commit-chain', {'message': message}))
        if 'error' in str(block): exit('Chain commit of message ' + message + ' failed - ' + str(block['error']))
        else: return block['result']

    def reveal_chain(self, entry):
        '''
        Reveal chain by entry
        :param entry: str, entry generated by compose
        :return: block['result']: transaction JSON block containing:
            message :"Entry Reveal Success"
            entryhash
            chainid
      '''
        block = json.loads(self.send_get_request_with_params_dict('reveal-chain', {'entry': entry}))
        if 'error' in str(block): exit('Chain reveal of entry ' + entry + ' failed - ' + str(block['error']))
        else: return block['result']

    def commit_entry(self, message):
        '''
        Commit entry by message
        :param message: str, entry generated by compose
        :return: block['result']: transaction JSON block containing:
            message:"Entry Commit Success"
            txid
            entryhash
        '''
        block = json.loads(self.send_get_request_with_params_dict('commit-entry', {'message': message}))
        if 'error' in str(block): exit('Entry commit of message ' + message + ' failed - ' + str(block['error']))
        else: return block['result']

    def reveal_entry(self, entry):
        '''
        Reveal entry by entry
        :param entry: str, entry generated by compose
        :return block['result']: transaction JSON block containing:
            message :"Entry Reveal Success"
            entryhash
            chainid
        '''
        block = json.loads(self.send_get_request_with_params_dict('reveal-entry', {'entry': entry}))
        if 'error' in str(block): exit('Chain reveal of entry ' + entry + ' failed - ' + str(block['error']))
        else: return block['result']

    def get_status(self, hash_or_tx_id, chain_id):
        '''
        This api call is used to find the status of a transaction, whether it be a factoid, reveal entry, or commit entry.
        chainid for factoid transaction is always 000...f, abbreviated to just f
        :return:
        Status types
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('ack', {'hash': hash_or_tx_id, 'chainid': chain_id}))
        return blocks["result"]

    def send_raw_message(self, message):
        '''
        Send raw message
        :param message: str, pure message to be injected into system
        :return: block['result']: JSON block containing:
            message :"Successfully sent the message"
      '''
        block = json.loads(self.send_get_request_with_params_dict('send-raw-message', {'message': message}))
        if 'error' in str(block): exit('Send raw message of ' + message + ' failed - ' + str(block['error']))
        else: return block['result']

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
        blocks = json.loads(self.send_get_request_with_params_dict('factoid-block', {'KeyMR': keymr}))
        return blocks['result']['fblock']

    def get_entrycredit_block_by_keymr(self, keymr):
        '''
        Get factoid block by keymr
        :param keymr: keymr
        :return: ecblock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entrycredit-block', {'KeyMR': keymr}))
        return blocks['result']['ecblock']


    def get_admin_block_by_keymr(self, keymr):
        '''
        Get factoid block by keymr
        :param keymr: keymr
        :return: ablock dict
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('admin-block', {'KeyMR': keymr}))
        return blocks['result']['ablock']
