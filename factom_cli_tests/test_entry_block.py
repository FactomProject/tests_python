import unittest
import logging
import ast
import re
import time
import datetime
import os
import threading

from random import randint
from nose.plugins.attrib import attr
from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.mail import send_email
from helpers.helpers import create_random_string, read_data_from_json
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server
from factom_cli_tests.loadnodes import LoadNodes
import re

class FactomEntryTests(unittest.TestCase):
    '''
    testcases to verify all the blocks(admin, directory, factoid, entrycredit) are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')

    factomd_address_prod = data['factomd_address_prod1']
    factomd_address_ansible = data['factomd_address']
    factomd_local =  data['localhost']

    factomd_address_custom_list = [data['factomd_address_0'],data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'],data['factomd_address_4'],
                                   data['factomd_address_5'],data['factomd_address_6'],
                                    data['factomd_address_7'], data['factomd_address_8'],
                                   data['factomd_address_9'], data['factomd_address_10']]
    factomd_followers_list = [data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]
    data = read_data_from_json('faulting.json')
    _stop_command = 'docker stop factom-factomd-i'
    _start_command = 'docker start factom-factomd-i'
    _delete_database = 'sudo rm -r /var/lib/docker/volumes/factom_base_factomd_data-i'
    _path_database = '/_data/m2/custom-database'

    def setUp(self):
        self.factom_chain_object = FactomChainObjects()
        self.factom_multiple_nodes = FactomHeightObjects()
        self.factom_cli_create = FactomCliCreate()
        self.factom_load_nodes = LoadNodes()
        self.missingentrycount = 0

    @attr(production=True)
    def notest_production_entries(self):
        self.missingentrycount = self._missing_entries(self.factomd_address_prod)
        print self.missingentrycount

    @attr(entry=True)
    def test_ansible_entries(self):
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
        self.entrycount = 0
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
                            print "server = %s, entryhash = %s" %(factomd_address,entryhash)
                        totalentries += 1
                        self.assertFalse(self.entrycontents == "Entry not found", ("missing entries %d" % totalentries))
        print "servers = %s, totalentries %d" % (factomd_address,totalentries)
        logging.getLogger('cli_command').info(totalentries)
        return self.entrycount
        self.assertTrue(entrycount == 0, "Missing entries in the block chain, missing entries: "+ str(entrycount))

    @attr(height=True)
    def notest_get_heights_of_all_nodes(self):
        msg = ""
        for x in range(0, 1000):
            for factomd_address_custom in self.factomd_address_custom_list:
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                result = self.factom_chain_object.get_heights()
                #print "height of server  : %s" % factomd_address_custom
                server = factomd_address_custom.replace(":8088","")
                output = ("SERVER          : %s" % server) + "\n" + result
                #print result
                msg =   msg + "\n" +  output + "\n"
            msg = msg + "\n" + "-------------------------------------------------------------------------------------------------"
            msg =  msg + "\n" + "datetime:" + str(datetime.datetime.now()) + "\n"
            logging.getLogger('Height').info(msg)
            time.sleep(3)
            print msg
            #send_email(msg)
            msg = ""



    def restart_followers(self):
        '''
        Test to synch blocks when audit servers and followers are rebooted
        :return:
        '''

        #entry_load =  threading.Thread(target= 'print "hello world"')
        #entry_load.start()

        for i in range(13,17):
            print i
            send_command_to_cli_and_receive_text(self._delete_database + str(i) + self._path_database)
        print "Restarting..."
        logging.getLogger('cli_command').info("Restarting")
        for i in range(13,17):
            print i
            send_command_to_cli_and_receive_text(self._stop_command + str(i))
            send_command_to_cli_and_receive_text(self._start_command + str(i))


    def sync_entry_height(self):
        #call the method to delete the database and restart the followers
        #self.restart_followers()
        #calculate the time taken for the followers to sync to the leader height
        starttime = time.time()
        found = True
        for factomd_address_custom in self.factomd_followers_list:
            while(found):
                time.sleep(10)
                self.factom_chain_object.change_factomd_address(factomd_address_custom)
                height = self.factom_chain_object.get_heights()
                while height.find("connection refused"):
                    height = self.factom_chain_object.get_heights()
                    break
                m1 = re.search(r'LeaderHeight: \d+',height)
                if m1:
                    leaderheight = m1.group(0)
                    leaderheight = leaderheight.replace("LeaderHeight: ","")
                m2 = re.search(r'EntryHeight: \d+',height)
                if m2:
                    entryheight = m2.group(0)
                    entryheight = entryheight.replace("EntryHeight: ","")
                    #elapsedtime =  time.time() - starttime
                #if elapsedtime > 6000:
                    #print "node hasn't synced for more than 5 mins, hence exiting"
                    #break
                if (leaderheight == entryheight) and leaderheight != str(0):
                    endtime = time.time()
                    timediff = endtime - starttime
                    print "timetaken to sync entry height to leader height %f" %timediff
                    logging.getLogger('cli_command').info("timetaken to sync entry height to leader height %f" %timediff)
                    found = True
                    break


    def loadtest(self):
        self.factom_load_nodes.make_chain_and_check_balance()
        return

    @attr(entrysync=True)
    def notest_load_with_height_check(self):
        t = threading.Thread(target=self.loadtest)
        t.start()
        self.sync_entry_height()

    def notest_entry_fetch(self):
        self.factom_load_nodes.make_chain_and_check_balance()

    def notest_directory_block(self):
        self.factom_chain_object.change_factomd_address(self.factomd_address_prod)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()
        for x in range(81000, int(directory_block_head)):
            directory_block_height = self.factom_chain_object.get_directory_block_height(str(x))
            self.assertFalse(directory_block_height == "Dblock not found","Dblock missing = %s" % (x))



