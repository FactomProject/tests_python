import re

from collections import defaultdict
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject

class FactomChainObjects(FactomBaseObject):
    _factomd_add_chain = 'addchain'
    _factomd_compose_chain = 'composechain '
    _factom_get_head = 'get head '
    _factom_get_heights = 'get heights'
    _factom_get_fbheight = 'get fbheight '
    _factom_get_abheight = 'get abheight '
    _factom_get_dbheight = 'get dbheight '
    _factom_get_ecbheight = 'get ecbheight '
    _factomd_compose_entry = 'composeentry '
    _factom_add_entries = 'addentry'
    _factom_get_firstentry = ' get firstentry '
    _factom_get_allentries = ' get allentries '
    _factom_pending_entries = 'get pendingentries '
    _factom_pending_transactions = 'get pendingtransactions '
    _factom_get_chainhead = ' get chainhead '
    _factom_wallet_backup_wallet = 'backupwallet'
    _factom_get_directoryblock = 'get dblock '
    _factom_get_entryblock = 'get eblock '
    _factom_get_entry_by_hash = 'get entry '
    _factom_get_raw = 'get raw '

    def parse_simple_data(self, text):
        return dict(item.split(": ") for item in text.split('\n'))

    def parse_entry_data(self, entry_text):
        entry_text = entry_text.split('\n')
        content = ' '.join([entry_text[-3], entry_text[-2]])
        del entry_text[-3:]
        entry_text.append(content)
        return dict(item.split(": ") for item in str(entry_text)[1:-1].translate(None, "'").split(', '))

    def parse_transaction_data(self, entry_text):
        entry_text = entry_text.split('\n')
        print entry_text
        del entry_text[-1:]
        print entry_text
        return dict(item.split(": ") for item in str(entry_text)[1:-1].translate(None, "'").split(', '))

    def parse_block_data(self, text):
        parsed_dict = defaultdict(list)
        starts = []
        ends = []
        lines = text.split("\n")

        for index, line in enumerate(lines):

            if ": " in line:
                line_parsed = line.split(": ")
                parsed_dict[line_parsed[0]] = line_parsed[1]

            elif "{" in line:
                starts.append(index)

            elif "}" in line:
                ends.append(index)

        final_repeated_list = []

        for start, end in zip(starts, ends):
            final_repeated_list.append(''.join(lines[start:end]))

        for elements in final_repeated_list:
            dict_parsing = elements.split(" {")
            parsed_dict[dict_parsing[0]].append(dict(x.split(' ') for x in dict_parsing[1].split('\t')[1:]))

        return parsed_dict

    def make_chain_from_binary_file(self, ecaddress, file_data, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' ', flags, ' ', chain_identifier, ' ', ecaddress, ' < ', file_data)))


    def make_chain_from_binary_data(self, ecaddress, data, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' ',
                                                             flags, ' ', chain_identifier, ' ', ecaddress)))

        return send_command_to_cli_and_receive_text(data)


    def compose_chain_from_binary_file(self, ecaddress, file_data, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_compose_chain, ' ', flags, ' ', chain_identifier, ' ', ecaddress, ' < ', file_data)))
        return text

    def add_entry_to_chain(self, ecaddress, file_data, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        return send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_add_entries, ' ', flags, ' ', chain_identifier, ' ', ecaddress, ' < ', file_data)))

    def compose_entry_from_binary_file(self, ecaddress, file_data, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factomd_compose_entry, ' ', flags, ' ', chain_identifier, ' ', ecaddress, ' < ', file_data)))
        return text

    def get_firstentry(self, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        elif 'chain_id' in kwargs:
            chain_identifier = kwargs['chain_id']
        return send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_get_firstentry, flags, ' ', chain_identifier)))

    def get_allentries(self, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        elif 'chain_id' in kwargs:
            chain_identifier = kwargs['chain_id']
        return send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_allentries, flags, ' ', chain_identifier)))

    def get_pending_entries(self, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_pending_entries, flags)))
        return text

    def get_pending_transactions(self, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        text = send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_pending_transactions, flags)))
        return text

    def get_chainhead(self, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])
        elif 'chain_id' in kwargs:
            chain_identifier = kwargs['chain_id']
        return send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_get_chainhead, flags, ' ', chain_identifier)))

    def get_latest_directory_block(self, **kwargs):
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_head, flags)))
        return text

    def get_heights(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_heights)))
        return text

    def get_directory_block_height_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_heights)))
        dict = self.parse_transaction_data(text)
        return dict['DirectoryBlockHeight']

    def get_factoid_block_by_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_fbheight, str(height))))
        return text

    def get_admin_block_by_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_abheight, str(height))))
        return text

    def get_directory_block_by_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_dbheight, str(height))))
        return text

    def get_entrycredit_block_by_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_ecbheight, str(height))))
        return text

    def get_directory_block(self, keymr):
        text = send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_get_directoryblock, keymr)))
        return text

    def get_entry_block(self,keymr):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_entryblock, keymr)))
        return text

    def get_entry_by_hash(self, entryhash):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_entry_by_hash, entryhash)))
        return text

    def get_raw(self, hash):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_raw, hash)))
        return text
