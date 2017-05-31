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
    _factom_get_chainhead = ' get chainhead '
    _factom_wallet_backup_wallet = 'backupwallet'
    _factom_get_directoryblock = 'get dblock '
    _factom_get_entryblock = 'get eblock '
    _factom_get_entryhash = 'get entry '

    def parse_chain_data(self, chain_text):
        return dict(item.split(": ") for item in chain_text.split('\n'))

    def parse_entry_data(self, entry_text):
        return dict(item.split(": ") for item in entry_text.split('\n'))

    def parse_first_entry_data(self, entry_text):
        entry_text = entry_text.split('\n')[:4]
        return dict(item.split(": ") for item in str(entry_text).split(','))

    def parse_summary_transaction_data(self, transaction_text):
        return dict(item.split(": ") for item in transaction_text.split('\n'))

    def parse_full_transaction_data(self, transaction_text):
        # strip blank line
        transaction_text = transaction_text[:-1]
        return dict(item.split(": ") for item in transaction_text.split('\n'))

    def parse_directoryblock_data(self, chainhead_text):
        # strip json
        chainhead_text = chainhead_text.split('\n')[:4]
        return dict(item.split(": ") for item in str(chainhead_text).split(','))

    def parse_directoryblock_minus_MR_data(self, chainhead_text):
        # strip json
        chainhead_text = chainhead_text.split('\n')[:3]
        return dict(item.split(": ") for item in str(chainhead_text).split(','))

    def parse_entryblock_data(self, chainhead_text):
        # strip json
        chainhead_text = chainhead_text.split('\n')[:6]
        return dict(item.split(": ") for item in str(chainhead_text).split(','))

    def make_chain_from_binary_file(self, ecaddress, file_data, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' ', flags, ' ', ext_to_string, ' ', ecaddress, ' < ', file_data)))

    def compose_chain_from_binary_file(self, ecaddress, file_data, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_compose_chain, flags, ' ', ext_to_string, ' ', ecaddress, ' < ', file_data)))
        return text

    def add_entry_to_chain(self, ecaddress, file_data, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_add_entries, ' ', flags, ' ',
                     ext_to_string, ' ', ecaddress, ' < ', file_data)))

    def compose_entry_from_binary_file(self, ecaddress, file_data, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factomd_compose_entry, flags, ' ', ext_to_string + ' ', ecaddress, ' < ', file_data)))
        return text

    def get_firstentry(self, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_firstentry, flags, ' ', ext_to_string)))

    def get_allentries(self, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_allentries, flags, ' ', ext_to_string)))

    def get_chainhead(self, external_id_with_flags_list, **kwargs):
        ext_to_string = ' '.join(external_id_with_flags_list)
        flags = ''
        if kwargs:
            flags = ' '.join(kwargs['flag_list'])
        return send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_chainhead, flags, ' ', ext_to_string)))


    def get_sequence_number_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_head)))
        return text.split('\n')[3].split(' ')[1]

    def get_latest_directory_block(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_head)))
        return text

    def get_directory_block_height_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_heights)))
        return text.split('\n')[0].split(' ')[1]

    def get_factoid_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_fbheight, height)))
        return text

    def get_admin_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_abheight, height)))
        return text

    def get_directory_block_by_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_dbheight, height)))
        return text

    def get_entrycredit_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_ecbheight, height)))
        return text

    def get_directory_block(self, keymr):
        text = send_command_to_cli_and_receive_text(
            ''.join((self._factom_cli_command, self._factom_get_directoryblock, keymr)))
        return text

    def get_entry_block(self,keymr):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_entryblock, keymr)))
        return text

    def get_entryhash(self,entryhash):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_entryhash, entryhash)))
        return text
