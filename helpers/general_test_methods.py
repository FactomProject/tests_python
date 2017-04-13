import time

from cli_objects.factom_cli_create import FactomCliCreate

def wait_for_ack(transaction_id, time_to_wait):
    factom_cli = FactomCliCreate()
    status = 'not found'
    i = 0

    while "TransactionACK" not in status and i < time_to_wait:
        status = factom_cli.request_transaction_acknowledgement(transaction_id)
        time.sleep(1)
        i += 1