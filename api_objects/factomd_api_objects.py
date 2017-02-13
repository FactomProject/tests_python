import requests
import json

from helpers.helpers import read_data_from_json


class FactomApiObjects():
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']

    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://'+self.factomd_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text, r.status_code

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        print r.text
        return r.text

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
        return blocks["result"]["entryblocklist"][0]

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

    def get_receipt_by_hash(self, hash):
        '''
        Get receip by hash
        :param hash: str hash
        :return: receipt
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('receipt', {'hash': hash}))
        return blocks['result']['Receipt']

    def get_entry_blcok(self, key_mr):
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
        Gets pemdomg emtroes
        :return: json with entryhash, chainid
        '''
        #TODO przetestuj params
        blocks = json.loads(self.send_get_request_with_method('pending-entries'))
        return blocks['result']

    def get_transaction_by_hash(self, hash):
        '''
        Gets transaction by transaction hash
        :param hash:
        :return: factoidtransaction json
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('transaction', {'hash': hash()}))
        return blocks['result']['factoidtransaction']

    def get_pending_transactions_by_address(self, address):
        '''
        Gets pending transaction by wallet address
        :param address: wallet adress
        :return: list with transaction ids and statuses
        '''

        blocks = json.loads(self.send_get_request_with_params_dict('pending-transactions', {'address': address}))
        return blocks['result']

    def get_chain_head_by_chain_id(self, chain_id):
        '''
        Gets chain head by chain id
        :param chain_id: str chain id
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('chain-head', {'ChainID': chain_id}))
        return blocks['result']['ChainHead']

    def get_entry_credits_balance_by_ec_address(self, ec_address):
        '''
        Gets entry credit balance by ec address
        :param ec_address: str - ec address
        :return: int - balance
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('entry-credit-balance', {'address': ec_address}))
        return blocks['result']['balance']

    def get_factoid_balance_by_factoid_address(self, factoid_address):
        '''
        Gets factoid balance by factoid address
        :param factoid_address: str address
        :return: int - balance
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factoid-balance', {'address': factoid_address})[0])
        return blocks['result']['balance']

    def get_entry_credits_rate(self):
        '''
        Gets entry credit rate
        :return: int - rate
        '''
        blocks = json.loads(self.send_get_request_with_method('entry-credit-rate'))
        return blocks#['result']['rate']

    def get_properties(self):
        '''
        Get properties
        :return: factomdversion, factomapiversion
        '''
        blocks = json.loads(self.send_get_request_with_method('properties'))
        return blocks['result']

    def submit_factoid_by_transaction(self, transaction):
        '''
        Submit factoid
        :param transaction: str, transaction hash
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('factoid-submit', {'transaction': transaction})[0])
        return blocks['result']

    def commit_chain_by_message(self, message):
        '''
        Commit chain by message
        :param message: str, message
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('commit-chain', {'message': message}))
        return blocks['result']

    def reveal_chain_by_entry(self, entry):
        '''
        Reveal chain by entry
        :param entry: str, entry
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('reveal-chain', {'entry': entry}))
        return blocks['result']

    def commit_entry(self, entry):
        '''
        Commit entry
        :param entry: str
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('commit-entry', {'entry': entry}))
        return blocks['result']

    def reveal_entry(self, entry):
        '''
        Commit entry
        :param entry: str
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('reveal-entry', {'entry': entry}))
        return blocks['result']

    def send_raw_message(self, message):
        '''
        Send raw message
        :param message: str message
        :return:
        '''
        blocks = json.loads(self.send_get_request_with_params_dict('send-raw-message', {'message': message}))
        return blocks['result']

