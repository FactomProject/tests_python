import shlex
from helpers.cli_methods import send_command_to_cli_and_receive_text
from cli_objects_base import CLIObjectsBase
from subprocess import Popen, PIPE

class CLIObjectsIdentityWallet(CLIObjectsBase):
    _add_chain = "identity addchain"
    _add_attribute = "identity addattribute"
    _add_attribute_endorsement = "identity addattributeendorsement"
    _new_identity = "newidentitykey"
    _list_identity_keys = "listidentitykeys"

    def make_identity_chain(self, ecaddress, content, pubkeys, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])
        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])

        # open subprocess as a way to 'write' content into the command instead of it coming from a file
        args = shlex.split(
            ''.join((self._cli_command, self._add_chain, ' ', flags, ' ', chain_identifier, ' ', ecaddress)))
        p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        text = p.communicate(content)
        '''
        separate output from status
        If all goes well, the output from the command will be in the 1st piece, followed by a null
        If an error occurs, the output of the command will be in the 2nd piece, preceded by a null
        '''
        text = text[0] if text[0] else text[1]
        # strip final line feed
        text = text[:-1]
        p.stdin.close()
        return text


    def new_identity_key(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._new_identity)))

    def list_identity_keys(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_identity_keys)))


