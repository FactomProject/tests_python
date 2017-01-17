import os

from helpers.helpers import read_data_from_json

class FactomBaseObject():
    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']
    factomd_address = data['factomd_address']
    _gopath = os.environ['GOPATH']
    _factom_cli_command = _gopath + '/src/github.com/FactomProject/factom-cli/factom-cli -w ' \
                                    ''+wallet_address+' -s '+factomd_address+' '
