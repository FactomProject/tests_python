from helpers.factom_cli_methods import send_command_to_cli_and_receive_text
from base_object import FactomBaseObject

class FactomChainObjects(FactomBaseObject):
    _factomd_add_chain = 'addchain '
    _factomd_compose_chain = 'composechain '
    _factom_get_head = 'get head '
    _factom_get_heights = 'get heights'
    _factom_get_fbheight = 'get fbheight '
    _factom_get_abheight = 'get abheight '
    _factom_get_dbheight = 'get dbheight '
    _factom_get_ecbheight = 'get ecbheight '
    _factomd_compose_entry = 'composeentry '
    _factom_add_entries = ' addentry '
    _factom_get_firstentry = ' get firstentry '
    _factom_get_allentries = ' get allentries '
    _factom_wallet_backup_wallet = 'backupwallet'
    _factom_get_entryblock = 'get eblock '
    _factom_get_entryhash = 'get entry '

    def make_chain_from_binary_file(self, ecadress, file_data, *external_ids):
        '''
        Make chain from binary data, external_ids should be string. there is no limit on external ids
        :param ecadress:
        :param file_data:
        :param external_ids:
        :return: text
        '''
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def parse_chain_data(self, chain_text):
        return dict(item.split(": ") for item in chain_text.split('\n'))

    def make_chain_from_binary_file_return_chain_id(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -C ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def make_chain_from_binary_file_return_entry_hash(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -E ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def make_chain_from_binary_file_return_tx_id(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -T ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def force_make_chain_from_binary_file(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -f ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def force_make_chain_from_binary_file_return_chain_id(self, ecadress, file_data, *external_ids):
        '''
         Make chain from binary data, external_ids should be string. there is no limit on external ids
         :param ecadress:
         :param file_data:
         :param external_ids:
         :return:
         '''
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -f ', ' -C ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def force_make_chain_from_binary_file_return_tx_id(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -f ', ' -T ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def quiet_make_chain_from_binary_file(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_add_chain, ' -q ',
                                                             ext_to_string + ' ', ecadress, ' < ', file_data)))

    def compose_chain_from_binary_file(self, ecadress, file_data, *external_ids):
        ext_to_string = ' '.join(['-n ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factomd_compose_chain, ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def add_entries_to_chain(self, ecaddress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-e ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_entries, ' -c ', chain_id , ' ', ext_to_string + ' ',
             ecaddress, ' < ', file_data)))
        return text

    def add_entries_to_chain_and_receive_tx_id(self, ecaddress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-e ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_entries, ' -c ', chain_id , ' ', ext_to_string + ' ',
             ecaddress, ' < ', file_data)))
        return text.split('\n')[0].split(' ')[1]

    def add_entries_to_chain_with_hex_ext_and_receive_tx_id(self, ecaddress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-x ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_entries, ' -c ', chain_id , ' ', ext_to_string + ' ',
             ecaddress, ' < ', file_data)))
        return text.split('\n')[0].split(' ')[1]

    def force_add_entries_to_chain(self, ecaddress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-e ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_entries, ' -f ', ' -c ', chain_id , ' ', ext_to_string + ' ',
             ecaddress, ' < ', file_data)))
        return text

    def force_add_entries_to_chain_and_receive_tx_id(self, ecaddress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-e ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_entries, ' -f ', ' -c ', chain_id , ' ', ext_to_string + ' ',
             ecaddress, ' < ', file_data)))
        return text.split('\n')[0].split(' ')[1]

    def force_add_entries_to_chain_with_hex_ext_and_receive_tx_id(self, ecaddress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-x ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_add_entries, ' -f ', ' -c ', chain_id , ' ', ext_to_string + ' ',
             ecaddress, ' < ', file_data)))
        return text.split('\n')[0].split(' ')[1]

    def compose_entry_from_binary_file(self, ecadress, file_data, chain_id, *external_ids):
        ext_to_string = ' '.join(['-e ' + s for s in external_ids])
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factomd_compose_entry, ' -c ', chain_id , ' ', ext_to_string + ' ', ecadress, ' < ', file_data)))
        return text

    def get_firstentry(self, chain_id):
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_firstentry, chain_id)))
        return text

    def get_firstentry_with_entryhash(self, chain_id):
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_firstentry, chain_id, ' -E ')))
        return text

    def get_allentries(self, chain_id):
        text = send_command_to_cli_and_receive_text(''.join(
            (self._factom_cli_command, self._factom_get_allentries, chain_id)))
        return text


    def get_sequence_number_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_head)))
        return text.split('\n')[3].split(' ')[1]

    def get_directory_block_height_from_head(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_heights)))
        return text.split('\n')[0].split(' ')[1]

    def get_factoid_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_fbheight, height)))
        return text

    def get_admin_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_abheight, height)))
        return text

    def get_directory_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_dbheight, height)))
        return text

    def get_entrycredit_block_height(self, height):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_ecbheight, height)))
        return text

    def get_entry_block(self,keymr):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_entryblock, keymr)))
        return text

    def get_entryhash(self,entryhash):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_entryhash, entryhash)))
        return text

    def get_heights(self):
        text = send_command_to_cli_and_receive_text(''.join((self._factom_cli_command, self._factom_get_heights)))
        return text