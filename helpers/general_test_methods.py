import time
import os

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers import read_data_from_json

cli_create = CLIObjectsCreate()
chain_objects = CLIObjectsChain()
data = read_data_from_json('shared_test_data.json')
blocktime = os.environ['BLOCKTIME']


BLOCK_WAIT_TIME = blocktime * 2
ACK_WAIT_TIME = 60

def wait_for_ack(transaction_id):
    for x in range(0, ACK_WAIT_TIME):
        if any(status in cli_create.request_transaction_acknowledgement(transaction_id) for status in ('TransactionACK', 'DBlockConfirmed')):
            break
        time.sleep(1)

def wait_for_chain_in_block(**kwargs):
    chain_identifier = ''
    if 'external_id_list' in kwargs:
        chain_identifier = ' '.join(kwargs['external_id_list'])
    for x in range(0, BLOCK_WAIT_TIME):
        result = chain_objects.get_chainhead(external_id_list=[chain_identifier])
        if 'Missing Chain Head' in result or 'Chain not yet included in a Directory Block' not in result: break
        time.sleep(1)
    return result

def fund_entry_credit_address(amount):
    # all entry credit addresses are funded from first_address
    first_address = cli_create.import_addresses(data['factoid_wallet_address'])[0]
    entry_credit_address = cli_create.create_entry_credit_address()
    text = cli_create.buy_entry_credits(first_address, entry_credit_address, str(amount))
    chain_dict = chain_objects.parse_simple_data(text)
    tx_id = chain_dict['TxID']
    wait_for_ack(tx_id)
    return entry_credit_address
