import requests
import commands
import logging
import time

def send_command_to_cli_and_receive_text(cli_command):
    ret = commands.getstatusoutput(cli_command)
    logging.getLogger('cli_command').info(cli_command)
    return ret[1]

def get_data_dump_from_server(server_address):
    data = {"item": "dataDump"}
    r = requests.get(server_address + '/factomd', params=data, auth=('relay','myunreachableyou'))
    return r.text

def wait_for_ack(self, transaction_id, time_to_wait):
    status = 'not found'
    i = 0
    while "TransactionACK" not in status and i < time_to_wait:
        status = self.factom_cli_create.request_transaction_acknowledgement(transaction_id)
        time.sleep(1)
        i += 1
