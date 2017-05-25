import time

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers import read_data_from_json

factom_cli_create = FactomCliCreate()
factom_chain_object = FactomChainObjects()
data = read_data_from_json('shared_test_data.json')
factom_cli = FactomCliCreate()
factom_object = FactomChainObjects()
# all entry credit addresses are funded from first_address
first_address = factom_cli_create.import_address_from_factoid(data['factoid_wallet_address'])
ACK_WAIT_TIME = 20
BLOCK_WAIT_TIME = 40

def wait_for_ack(transaction_id):
    status = 'not found'
    i = 0

    while "TransactionACK" not in status and i < ACK_WAIT_TIME:
        status = factom_cli.request_transaction_acknowledgement(transaction_id)
        time.sleep(1)
        i += 1

def wait_for_entry_in_block(chain):
    '''****************************************************
    Invalid Hash is an error in factomd coding and will corrected in the future to the correct message.
    When it is corrected, change it here to match the new message.
    *******************************************************'''

    status = 'Invalid Hash'
    i = 0

    while "Invalid Hash" in status and i < BLOCK_WAIT_TIME:
        status = factom_object.get_chainhead(chain)
        time.sleep(1)
        i += 1

def fund_entry_credit_address(amount):
    # all entry credit addresses are funded from first_address
    entry_credit_address = factom_cli_create.create_entry_credit_address()
    text = factom_cli_create.buy_ec(first_address, entry_credit_address, str(amount))
    chain_dict = factom_chain_object.parse_summary_transaction_data(text)
    tx_id = chain_dict['TxID']
    wait_for_ack(tx_id)
    return entry_credit_address
