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
BLOCK_WAIT_TIME = 50

def wait_for_ack(transaction_id):
    for x in range(0, BLOCK_WAIT_TIME):
        if 'TransactionACK' in factom_cli.request_transaction_acknowledgement(transaction_id): break
        time.sleep(1)

def wait_for_entry_in_block(**kwargs):
    chain_identifier = ''
    if 'external_id_list' in kwargs:
        chain_identifier = ' '.join(kwargs['external_id_list'])

    # TODO replace Invalid Hash with correct error message once it is corrected in code

    for x in range(0, BLOCK_WAIT_TIME):
        if 'Invalid Hash' not in factom_object.get_chainhead(external_id_list=[chain_identifier]): break
        time.sleep(1)

def fund_entry_credit_address(amount):
    # all entry credit addresses are funded from first_address
    entry_credit_address = factom_cli_create.create_entry_credit_address()
    text = factom_cli_create.buy_ec(first_address, entry_credit_address, str(amount))
    chain_dict = factom_chain_object.parse_simple_data(text)
    tx_id = chain_dict['TxID']
    wait_for_ack(tx_id)
    return entry_credit_address
