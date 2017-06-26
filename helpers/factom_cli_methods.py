import requests
import commands
import logging

def send_command_to_cli_and_receive_text(cli_command):
    print cli_command
    ret = commands.getstatusoutput(cli_command)
    print ret[1]
    # logging.getLogger('cli_command').info(cli_command)
    return ret[1]


def get_data_dump_from_server(server_address):
    data = {"item": "dataDump"}
    r = requests.get(server_address + '/factomd', params=data, auth=('relay','myunreachableyou'))
    return r.text