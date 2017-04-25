import unittest
import logging
import ast
import time
import datetime
import threading

from nose.plugins.attrib import attr
from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_multiple_nodes import FactomHeightObjects
from cli_objects.factom_chain_objects import FactomChainObjects
from helpers.helpers import create_random_string, read_data_from_json
from helpers.factom_cli_methods import send_command_to_cli_and_receive_text, get_data_dump_from_server
from factom_cli_tests.loadnodes import LoadNodes
import re

class FactomEntryTests(unittest.TestCase):
    '''
    testcases to verify all entries are the same in every node in the network
    '''
    data = read_data_from_json('addresses.json')
    factomd_address_prod = data['factomd_address_prod1']
    factomd_address_custom_list = [data['factomd_address'],data['factomd_address_0'],data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'],data['factomd_address_4'],
                                   data['factomd_address_5'],data['factomd_address_6']]
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
        self.totalentries = 0
        self.entrycountlist = []

    @attr(production=True)
    def test_production_entries(self):
        self.missingentrycount = self._missing_entries(self.factomd_address_prod)

    @attr(load=True)
    def test_ansible_entries(self):
        for factomd_address_custom in self.factomd_address_custom_list:
            self.entrycountlist.append(self._missing_entries(factomd_address_custom))
        self.assertTrue(all(x == self.entrycountlist[0] for x in self.entrycountlist),"mismatch in entries of the servers")

    def _missing_entries(self, factomd_address):
        self.factom_chain_object.change_factomd_address(factomd_address)
        directory_block_head = self.factom_chain_object.get_directory_block_height_from_head()
        self.totalentries = 0
        self.missingentrycount = 0
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
                            self.missingentrycount += 1
                        self.totalentries += 1
                        self.assertFalse(self.missingentrycount > 0, ("missing entries = %d on server = %s" % (self.missingentrycount,factomd_address)))
        logging.getLogger('cli_command').info("total entries = %d on server = %s",(self.totalentries,factomd_address))
        return self.totalentries

    def restart_followers(self):
        '''
        Test to synch blocks when audit servers and followers are rebooted
        :return:
        '''
        for i in range(13,17):
            send_command_to_cli_and_receive_text(self._delete_database + str(i) + self._path_database)
        logging.getLogger('cli_command').info("Restarting audit servers and followers")
        for i in range(13,17):
            send_command_to_cli_and_receive_text(self._stop_command + str(i))
            send_command_to_cli_and_receive_text(self._start_command + str(i))


    def sync_entry_height(self):
        #call the method to delete the database and restart the followers
        self.restart_followers()
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
                    elapsedtime =  time.time() - starttime
                    if (leaderheight == entryheight) and leaderheight != str(0):
                        endtime = time.time()
                        timediff = endtime - starttime
                        logging.getLogger('cli_command').info(
                            "timetaken to sync entry height to leader height %f" % timediff)
                        found = True
                        break
                    elif elapsedtime > 600:
                        logging.getLogger('cli_command').info("node hasn't synced for more than 10 mins, hence exiting")
                        break


    def loadtest(self):
        self.factom_load_nodes.make_chain_and_check_balance()
        return

    @attr(load=True)
    def notest_load_with_height_check(self):
        t = threading.Thread(target=self.loadtest)
        t.start()
        self.sync_entry_height()
