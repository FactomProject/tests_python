import random
import string
import json
import os
import time

def create_random_string(char_nr):
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_nr))

def read_data_from_json(file_name):
    """
    Parse json
    :param file_name: json file
    :return: parsed json
    """
    directory = os.path.dirname(__file__)
    filename = os.path.join(directory, '../test_data/'+file_name)

    with open(filename) as f:
        json_data = f.read()
        return json.loads(json_data)

def wait_for_ack(self, transaction_id, time_to_wait):
    status = 'not found'
    i = 0
    while "TransactionACK" not in status and i < time_to_wait:
        status = self.factom_cli_create.request_transaction_acknowledgement(transaction_id)
        time.sleep(1)
        i += 1
    return status













