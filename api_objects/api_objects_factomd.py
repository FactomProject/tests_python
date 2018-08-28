import requests, json, ast, time

from helpers.helpers import read_data_from_json
from requests.exceptions import HTTPError

class APIObjectsFactomd():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def send_get_request_with_params_dict(self, method, params_dict, repeatOK=False):
        url = 'http://'+self.factomd_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        self.raise_for_status_with_message(method, r, repeatOK)
        return r.text

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        self.raise_for_status_with_message(method, r)
        return r.text

    def raise_for_status_with_message(self, method, response, repeatOK=False):
        """
        expand raise_for_status method to return helpful error message
        :param response: JSON, requests response object
        :param repeatOK: boolean, True means do not throw error if Repeated Commit is detected
        """
        try:
            response.raise_for_status()
        except HTTPError as error:
            if response.text:
                if not repeatOK or 'Repeated Commit' not in str(response.text):
                    raise HTTPError('{} Error Message: {}'.format(str(error.message), 'API-call ' + method + ' failed - ' + response.text))
            else:
                raise error
        return

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
        return block['result']

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
        return block['result']['balance']

    def multiple_ec__balances(self, *ec_addresses):
        '''
        Gets entry credit balances for multiple ec addresses
        :param *ec addresses: list, 1 or more ec addresses
        :return: list of lists [acknowledged balance, saved balance (in entry credits)], one list for each input address
        :return: int, last saved block height at which balances were detected
        :return: int, current block being created at which balances were detected
        '''
        block = json.loads(self.send_get_request_with_params_dict('multiple-ec-balances', ast.literal_eval(
            json.dumps({'addresses': [ec_address for ec_address in ec_addresses]}))))
        return block['result']['balances'], block['result']['lastsavedheight'], block['result']['currentheight']

    def get_factoid_balance(self, factoid_address):
        '''
        Gets factoid balance by factoid address
        :param factoid_address: str, address of which to return balance
        :return: int, balance
        '''
        block = json.loads(self.send_get_request_with_params_dict('factoid-balance', {'address': factoid_address}))
        return block['result']['balance']

    def multiple_fct__balances(self, *fct_addresses):
        '''
        Gets factoid balances for multiple factoid addresses
        :param *fct addresses: list, 1 or more factoid addresses
        :return: list of lists [acknowledged balance, saved balance (in factoshis), error message], one list for each input address
        :return: int, last saved block height at which balances were detected
        :return: int, current block being created at which balances were detected
        '''
        block = json.loads(self.send_get_request_with_params_dict('multiple-fct-balances', ast.literal_eval(json.dumps({'addresses': [fct_address for fct_address in fct_addresses]}))))
        return block['result']['balances'], block['result']['lastsavedheight'], block['result']['currentheight']

    def get_entry_credit_rate(self):
        '''
        Gets entry credit rate
        :return int, how many factoshis it currently takes to create an entry credit
        '''
        block = json.loads(self.send_get_request_with_method('entry-credit-rate'))
        return block['result']['rate']

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
        return block['result']

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
        return block['result']

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
        return block['result']

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
        return block['result']

    def get_status(self, hash_or_tx_id, chain_id):
        '''
        This api_factomd call is used to find the status of a transaction, whether it be a factoid, reveal entry, or commit entry.
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
        return block['result']

    def get_current_minute(self):
        '''
        Get current minute of the directory block
        :return: current minute currentblocktime
        '''
        block = json.loads(self.send_get_request_with_method('current-minute'))
        return block['result']['minute']

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


    def calculate_blocktime(self):
        minuteinitial = self.get_current_minute()

        # get time of fresh minute
        for seconds in range(601):
            minutestart = self.get_current_minute()
            if minutestart != minuteinitial:
                timestart = time.time()
                break
            else:
                time.sleep(1)
        if seconds == 600: exit('Minute is over 600 seconds')

        # get time of next minute
        for seconds in range(601):
            nextminutestart = self.get_current_minute()
            if nextminutestart != minutestart:
                timenext = time.time()
                break
            else:
                time.sleep(1)
        if seconds == 600: exit('Minute is over 600 seconds')
        return int(10 * round(timenext - timestart))


