from helpers.cli_methods import send_command_to_cli_and_receive_text
from cli_objects_base_ import CLIObjectsBase
from helpers.helpers import read_data_from_json

class CLIObjectsMultipleNodes(CLIObjectsBase):
    _get_head = ' get head '
    _get_heights = ' get heights'
    _get_fbheight = ' get fbheight '
    _get_abheight = ' get abheight '
    _get_dbheight = ' get dbheight '
    _get_ecbheight = ' get ecbheight '
    _get_walletheight = ' get walletheight '
    _list_transactions = ' listtxs '

    data = read_data_from_json('addresses.json')

    def get_wallet_height(self):
        text = send_command_to_cli_and_receive_text(''.join((self._cli_command, self._get_walletheight)))
        return text.split('\n')[0].split(' ')[1]

    def get_all_transactions(self):
        text = send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_transactions)))
        return text