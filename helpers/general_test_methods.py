import time
import os

from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_chain import CLIObjectsChain
from helpers import read_data_from_json

from api_objects.api_objects_factomd import APIObjectsFactomd

cli_create = CLIObjectsCreate()
chain_objects = CLIObjectsChain()

api_objects_factomd = APIObjectsFactomd()

data = read_data_from_json('shared_test_data.json')
blocktime = int(os.environ['BLOCKTIME'])


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
        # kwargs['external_id_list'].insert(0, '-h')
        # kwargs['external_id_list'].insert(2, '-h')
        chain_identifier = ' '.join(kwargs['external_id_list'])
    for x in range(0, BLOCK_WAIT_TIME):
        result = chain_objects.get_chainhead(external_id_list=[chain_identifier])
        if 'Missing Chain Head' not in result and 'Chain not yet included in a Directory Block' not in result: break
        time.sleep(1)
    return result

def fund_entry_credit_address(amount):
    '''
    create an entry credit addresses and fund it with <amount> entry credits from primary factoid address
    :param: int, number of entry credits to convert from factoid address to new entry credit address
    :return: str, newly created entry credit address
  '''
    first_address = cli_create.import_addresses(data['factoid_wallet_address'])[0]
    balance = api_objects_factomd.get_factoid_balance(first_address)
    factoshi_amount = amount * api_objects_factomd.get_entry_credit_rate()
    if int(balance) < factoshi_amount: exit('Factoid address ' + first_address + ' only has ' + balance + ' factoshis but needs ' + str(factoshi_amount) + ' to buy ' + amount + ' entry credits')
    else:
        entry_credit_address = cli_create.create_entry_credit_address()
        text = cli_create.buy_entry_credits(first_address, entry_credit_address, str(amount))
        chain_dict = chain_objects.parse_simple_data(text)
        tx_id = chain_dict['TxID']
        wait_for_ack(tx_id)
    return entry_credit_address
