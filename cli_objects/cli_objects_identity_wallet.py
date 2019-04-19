import shlex
from helpers.cli_methods import send_command_to_cli_and_receive_text
from .cli_objects_base import CLIObjectsBase
from subprocess import Popen, PIPE

class CLIObjectsIdentityWallet(CLIObjectsBase):
    _add_identity_chain = "identity addchain "
    _add_attribute = "identity addattribute "
    _add_attribute_endorsement = "identity addattributeendorsement "
    _new_identity = "newidentitykey "
    _list_identity_keys = "listidentitykeys "
    _rm_identity_key = "rmidentitykey "
    _identity_get_active_keys = "identity getactivekeys "
    _identity_key_replacement = "identity addkeyreplacement "



    def add_identity_chain(self, ecaddress, content, **kwargs):
        flags = ''
        if 'flag_list' in kwargs:
            flags = ' '.join(kwargs['flag_list'])

        chain_identifier = ''
        if 'external_id_list' in kwargs:
            chain_identifier = ' '.join(kwargs['external_id_list'])

        if 'public_key_list' in kwargs:
            key_list = ' '.join(kwargs['public_key_list'])

        # open subprocess as a way to 'write' content into the command instead of it coming from a file
        args = shlex.split(
            ''.join((self._cli_command, self._add_identity_chain, ' ',  chain_identifier, ' ', flags, ' ', key_list , ' ' , ecaddress)))
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
        return text.decode('utf-8')


    def new_identity_key(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._new_identity)))


    def list_identity_keys(self):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._list_identity_keys)))


    def rm_identity_key(self,identity):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command,self._rm_identity_key, identity)))


    def add_attribute(self,chainid,receiver_chainid, signer_chainid, signer_pubkey, attribute, ecaddress):

        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._add_attribute, ' -c ', chainid, ' -creceiver ', receiver_chainid, ' -csigner ', signer_chainid, ' -signerkey ', signer_pubkey
                                                             , ' -attribute ', attribute, ' ',  ecaddress)))


    def get_keys_at_height(self,chainid, height):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._identity_get_active_keys, ' -c ', chainid, ' ' , height)))



    def add_attribute_endorsement(self,chainid, signer_chainid, signer_pubkey, entryhash, ecaddress):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._add_attribute_endorsement, ' -c ', chainid, ' -csigner ', signer_chainid, ' -signerkey ', signer_pubkey
                                                             , ' -entryhash ', entryhash, ' ',  ecaddress)))

    def add_key_replacement(self,chainid,oldkey,newkey,signerkey,ecaddress):
        return send_command_to_cli_and_receive_text(''.join((self._cli_command, self._identity_key_replacement, ' -c ', chainid, ' --oldkey ', oldkey, ' --newkey ', newkey, ' --signerkey ', signerkey, ' ', ecaddress)))
