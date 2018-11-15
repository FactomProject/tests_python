import unittest, os, binascii, time

from helpers.helpers import create_random_string

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from cli_objects.cli_objects_identity_wallet import CLIObjectsIdentityWallet
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import wait_for_ack, wait_for_chain_in_block, fund_entry_credit_address, wait_for_entry_in_block

@attr(fast=True)
class CLITestsChains(unittest.TestCase):
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    cli_identity = CLIObjectsIdentityWallet()
    api_factomd = APIObjectsFactomd()
    data = read_data_from_json('shared_test_data.json')
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']

    TIME_TO_WAIT = 5

    passphrase =  "main"
    timeout = "1"

    def unlock_wallet(self):
        result = self.cli_create.unlock_wallet(self.passphrase,self.timeout)
        return result

    def test_list_addresses(self):
        for i in range(1,1000):
            print self.cli_create.list_addresses()
            result = self.unlock_wallet()
            if result == "Incorrect passphrase":
                print result
                exit()
            else:
                print self.cli_create.list_addresses()


    def test_get_entrycredit_rate(self):
        ec_rate = self.cli_create.get_entry_credit_rate()
        result = self.unlock_wallet()
        if result == "Incorrect passphrase" or result == "Wallet is locked":
            print result
            exit()
        else:
            ec_rate = self.cli_create.get_entry_credit_rate()


    def test_new_address(self):
        # new fct address
        result =  self.cli_create.create_new_factoid_address()
        print result
        self.assertIn("Wallet is locked", result, "Wallet is not locked. Result returned is " + str(result))

        result = self.unlock_wallet()
        print result
        self.assertNotIn("Incorrect passphrase", result, "Unlocking the wallet failed")

        result = self.cli_create.create_new_factoid_address()
        print result
        self.assertNotIn("Wallet is locked", result, "Wallet should not be locked. Result returned is " + str(result))

        # new ec address
        self.cli_create.create_entry_credit_address()
        result = self.unlock_wallet()
        if result == "Incorrect passphrase":
            exit()
        else:
            self.cli_create.create_entry_credit_address()

        result = self.unlock_wallet()
        # new import address
        result = self.cli_create.import_addresses(self.data['factoid_wallet_address'])
        print result
        self.assertNotIn("Wallet is locked",result,"Wallet is not locked. Result returned is " +  str(result))


        result = self.cli_create.import_addresses(self.data['ec_wallet_address'])
        print result
        self.assertNotIn("Wallet is locked", result, "Wallet is not locked. Result returned is " + str(result))


    def test_address(self):

        for i in range(1,1000):
            result = self.cli_create.create_new_factoid_address()
            print result
            self.assertIn("Wallet is locked", result, "Wallet is not locked. Result returned is " + str(result))

            result = self.unlock_wallet()
            print result
            self.assertNotIn("Incorrect passphrase", result, "Unlocking the wallet failed")

            result = self.cli_create.create_new_factoid_address()
            print result
            self.assertNotIn("Wallet is locked", result,
                             "Wallet should not be locked. Result returned is " + str(result))

            time.sleep(2)