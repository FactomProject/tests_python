import unittest, os, binascii, time

from nose.plugins.attrib import attr
#from api_objects.api_objects_factomd import APIObjectsFactomd
#from cli_objects.cli_objects_chain import CLIObjectsChain
#from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_identity_wallet import CLIObjectsIdentityWallet
#from helpers.helpers import create_random_string, read_data_from_json
#from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address

@attr(fast=True)
class CLITestsChains(unittest.TestCase):
    #cli_chain = CLIObjectsChain()
    #cli_create = CLIObjectsCreate()
    cli_identity = CLIObjectsIdentityWallet()
    #api_factomd = APIObjectsFactomd()
    #blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    #data = read_data_from_json('shared_test_data.json')

    #TIME_TO_WAIT = 5


    def test_new_identity_key(self):
        print self.cli_identity.new_identity_key()

    def test_list_all_identity_keys(self):
        newkey = self.cli_identity.new_identity_key()
        keylist =  (self.cli_identity.list_identity_keys()).split()

        for i in range(0, len(keylist)-1):
            #print "key = " + keylist[i]
            if newkey == keylist[i]:
                print "found the key"

    # def test_make_chain_and_check_chainhead(self):
    #     self.entry_credit_address100 = fund_entry_credit_address(100)
    #     data = create_random_string(1024)
    #     path = os.path.join(os.path.dirname(__file__), self.data['test_file_path'])
    #     name_1 = create_random_string(5)
    #     name_2 = create_random_string(5)
    #     names_list = ['-n', name_1, '-n', name_2]
    #     chain_flag_list = ['-f', '-C']
    #
    #     chainid = self.cli_chain.make_chain(self.entry_credit_address100, data, external_id_list=names_list,
    #                                         flag_list=chain_flag_list)
    #     found = False
    #     for x in range(0, self.TIME_TO_WAIT):
    #         if 'Chain not yet included in a Directory Block' in self.cli_chain.get_allentries(chain_id=chainid):
    #             found = True
    #             break
    #         time.sleep(1)
    #     self.assertTrue(found, 'Chainhead is missing')
    #     for x in range(0, self.blocktime):
    #         if 'Chain not yet included in a Directory Block' not in self.cli_chain.get_allentries(chain_id=chainid):
    #             found = True
    #             break
    #         time.sleep(1)