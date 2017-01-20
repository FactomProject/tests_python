from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject

import os


class FactomChainObjects(FactomBaseObject):
    _factomd_add_chain = 'addchain '
    _factom_get_head = 'get head '
    _factom_get_heights = 'get heights'
    _factom_add_entries = ' addentry '
    _factom_get_entry = ' get entry '

    def make_chain_from_binary_file(self, ecadress, file_data, *external_ids):
        '''
        Make chain from binary data, external_ids should be string. there is no limit on external ids
        :param ecadress:
        :param file_data:
        :param external_ids:
        :return:
        '''
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text.split('\n')[1].split(' ')[1]


    def force_make_chain_from_binary_file_and_receiv_chain_id(self, ecadress, file_data, *external_ids):
        '''
        Make chain from binary data, external_ids should be string. there is no limit on external ids
        :param ecadress:
        :param file_data:
        :param external_ids:
        :return:
        '''
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -f ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text.split('\n')[1].split(' ')[1]

    def get_sequence_number_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_head)))
        return text.split('\n')[3].split(' ')[1]

    def get_directory_block_height_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_heights)))
        return text.split('\n')[0].split(' ')[1]

    def add_entries_to_chain_and_receive_entry_hash(self, ecadress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_add_entries, ' -c ', chain_id , ' ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text.split('\n')[2].split(' ')[1]

    def get_entries_by_hash(self, hash):
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_entry, ' ', hash)))
        return text
