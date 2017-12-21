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
        chain_identifier = ' '.join(kwargs['external_id_list'])
    for x in range(0, BLOCK_WAIT_TIME):
        result = chain_objects.get_chainhead(external_id_list=[chain_identifier])
        if 'Missing Chain Head' in result or 'Chain not yet included in a Directory Block' not in result: break
        time.sleep(1)
    return result

def fund_entry_credit_address(amount):
    '''
    create an entry credit addresses and fund it with <amount> entry credits from primary factoid address
    :param amount: int, number of entry credits to convert from factoid address to new entry credit address
    :return: return_data: str,
        if API call succeeds, newly created entry credit address
        if fetching balance of primary factoid address fails, returned balance
        if fetching entry credit rate fails, returned entry credit rate
        if factoid address balance is less than needed, shortfall
    :return error_message: if API call succeeds, nil
    if API call fails, useful error message
  '''
    first_address = cli_create.import_addresses(data['factoid_wallet_address'])[0]
    balance, error_message = api_objects_factomd.get_factoid_balance(first_address)
    return_data = balance
    if not error_message:
        entry_credit_rate, error_message = api_objects_factomd.get_entry_credit_rate()
        if error_message:
            return_data = entry_credit_rate
        else:
            factoshi_amount = amount * entry_credit_rate['rate']
            if int(balance['balance']) < factoshi_amount:
                error_message = 'Factoid address ' + first_address + ' only has ' + balance['balance'] + ' factoshis and needs ' + str(factoshi_amount) + ' to buy ' + amount + ' entry credits'
            else:
                entry_credit_address = cli_create.create_entry_credit_address()
                text = cli_create.buy_entry_credits(first_address, entry_credit_address, str(amount))
                chain_dict = chain_objects.parse_simple_data(text)
                tx_id = chain_dict['TxID']
                wait_for_ack(tx_id)
                return_data = entry_credit_address
    return return_data, error_message
