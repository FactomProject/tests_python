import os

from helpers.helpers import read_data_from_json

class FactomBaseObject():
    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']
    _factomd_address = data['factomd_address']
    _gopath = os.environ['GOPATH']
    _factom_cli_command = _gopath + '/src/github.com/FactomProject/factom-cli/factom-cli -w ' \
                                    '' + wallet_address + ' -s ' + _factomd_address + ' '

    def change_factomd_address(self, value):
        self._factom_cli_command = self._gopath + '/src/github.com/FactomProject/factom-cli/factom-cli -w ' \
                                                  '' + self.wallet_address + ' -s ' + value + ' '
