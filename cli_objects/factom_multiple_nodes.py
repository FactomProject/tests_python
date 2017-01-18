from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject

class FactomHeightObjects(FactomBaseObject):
    _factom_get_head = 'get head '
    _factom_get_heights = 'get heights'
    _factom_add_entries = ' addentry '
    _factom_get_fbheight = 'get fbheight '
    _factom_get_abheight = 'get abheight '
    _factom_get_dbheight = 'get dbheight '
    _factom_get_ecbheight = 'get ecbheight '

    def get_entrycredit_block_height_custom(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, self._factom_get_ecbheight, height)))
        return text

    def get_admin_block_height_custom(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, self._factom_get_abheight, height)))
        return text


    def get_directory_block_height_custom(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, self._factom_get_dbheight, height)))
        return text

    def get_factoid_block_height_custom(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command_custom, self._factom_get_fbheight, height)))
        return text