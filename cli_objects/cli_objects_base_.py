import os

from helpers.helpers import read_data_from_json

class CLIObjectsBase():
    data = read_data_from_json('addresses.json')
    wallet_address = data['wallet_address']
    factomd_address = data['factomd_address']
    factomd_address_2 = data['factomd_address_2']

    #_gopath = os.environ['GOPATH']
    _cli_command = '/srv/factom-cli -w ' \
                                  '' + wallet_address +' -s ' + factomd_address +' '

    def change_factomd_address(self, value):
        self._cli_command = '/srv/factom-cli -w ' \
                                                 '' + self.wallet_address + ' -s ' + value + ' '

