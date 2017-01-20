import os

from helpers.helpers import read_data_from_json

class FactomBaseObject():
    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']
    factomd_address = data['factomd_address']
    factomd_address_2 = data['factomd_address_2']

    _gopath = os.environ['GOPATH']
    _factom_cli_command = '/home/veena/go/bin/factom-cli -w ' \
                                    ''+wallet_address+' -s '+factomd_address+' '
    _factom_cli_command_custom = '/home/veena/go/bin/factom-cli -w ' \
                                    ''+wallet_address+' -s '
