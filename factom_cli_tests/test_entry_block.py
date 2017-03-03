import unittest

from nose.plugins.attrib import attr

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import read_data_from_json
from helpers.mail import send_email
import ast
import re
import time
import datetime

class FactomEntryTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')

    factomd_address_prod = data['factomd_windows_laptop']
    factomd_address_ansible = data['factomd_address']
    factomd_address_custom_list = [data['factomd_address'], data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
                                   data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
                                   data['factomd_address_6']]

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        self.missingentrycount = 0

    #@attr(production=True)
    def notest_production_entries(self):
        self.missingentrycount = self._missing_entries(self.factomd_address_prod)
        print self.missingentrycount

    @attr(fast=True)
    def notest_ansible_entries(self):
        for factomd_address_custom in self.factomd_address_custom_list:
            self._missing_entries(factomd_address_custom)
            print "total entrycount missing = %d on the server = %s" % (self.entrycount, factomd_address_custom)
            self.entrycount = 0


    def _missing_entries(self, factomd_address):
        self.factom_cli_create.change_factomd_address(factomd_address)
        self.factom_multiple_nodes.change_factomd_address(factomd_address)
        self.factom_chain_object.change_factomd_address(factomd_address)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()
        totalentries = 0
        for x in range(0, int(directory_block_head)):
            directory_block_height = self.factom_chain_object.get_directory_block_height(str(x))
            directory_block_height = ast.literal_eval(directory_block_height)
            if len(directory_block_height['dblock']['dbentries']) > 3:
                totalentryblocks = len(directory_block_height['dblock']['dbentries'])
                for x in range(3, totalentryblocks):
                    keymr = directory_block_height['dblock']['dbentries'][x]['keymr']
                    entryblock =  self.factom_chain_object.get_entry_block(keymr)
                    entryblock = "".join(entryblock.split())
                    pattern = re.compile('EntryHash.{64}')
                    entryblocklist = pattern.findall(entryblock)
                    for entryhash in entryblocklist:
                        entryhash = entryhash.replace("EntryHash","")
                        self.entrycontents = self.factom_chain_object.get_entryhash(entryhash)
                        if (self.entrycontents == "Entry not found"):
                            self.entrycount += 1
                        totalentries += 1
                        #self.assertFalse(entrycontents == "Entry not found", ("missing entries %d" % entrycount))
        print "totalentries %d" % totalentries
        return self.entrycount
        #self.assertTrue(entrycount == 0, "Missing entries in the block chain, missing entries: "+ str(entrycount))


    def test_get_heights_of_all_nodes(self):
        msg = ""
        for x in range(0, 5):
            for factomd_address_custom in self.factomd_address_custom_list:
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                result = self.factom_chain_object.get_heights()
                #print "height of server  : %s" % factomd_address_custom
                output = ("height of server  : %s" % factomd_address_custom) + "\n" + result
                #print result
                msg =   msg + "\n" +  output + "\n"
            msg = msg + "\n" + "-------------------------------------------------------------------------------------------------"
            time.sleep(3)
            msg =  msg + "\n" + "datetime:" + str(datetime.datetime.now()) + "\n"
            print msg
            send_email(msg)
            msg = ""



