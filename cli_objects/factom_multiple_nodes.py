from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject
from helpers.helpers import read_data_from_json

class FactomHeightObjects(FactomBaseObject):
    _factom_get_head = ' get head '
    _factom_get_heights = ' get heights'
    _factom_get_fbheight = ' get fbheight '
    _factom_get_abheight = ' get abheight '
    _factom_get_dbheight = ' get dbheight '
    _factom_get_ecbheight = ' get ecbheight '
    _factom_get_walletheight = ' get walletheight '
    _factom_list_transactions = ' listtxs '

    data = read_data_from_json('addresses.json')

    def get_wallet_height(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_walletheight)))
        return text.split('\n')[0].split(' ')[1]

    def get_all_transactions(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_list_transactions)))
        return text