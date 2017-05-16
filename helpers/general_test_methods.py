import time

from cli_objects.factom_cli_create import FactomCliCreate

ACK_WAIT_TIME = 20

def wait_for_ack(transaction_id):
    factom_cli = FactomCliCreate()
    status = 'not found'
    i = 0

    while "TransactionACK" not in status and i < ACK_WAIT_TIME:
        status = factom_cli.request_transaction_acknowledgement(transaction_id)
        time.sleep(1)
        i += 1