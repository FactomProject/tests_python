from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject
from helpers.helpers import create_random_string, read_data_from_json

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


    def get_entrycredit_block_height_custom(self, factomd_addr, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, factomd_addr, self._factom_get_ecbheight, height)))
        return text

    def get_admin_block_height_custom(self, factomd_addr, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, factomd_addr, self._factom_get_abheight, height)))
        return text


    def get_directory_block_height_custom(self, factomd_addr, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, factomd_addr, self._factom_get_dbheight, height)))
        return text

    def get_factoid_block_height_custom(self,factomd_addr, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, factomd_addr, self._factom_get_fbheight, height)))
        return text

    def get_wallet_height(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_walletheight)))
        return text.split('\n')[0].split(' ')[1]


    def get_all_transactions(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_list_transactions)))
        return text

