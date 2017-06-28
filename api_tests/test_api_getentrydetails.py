import unittest
import time
import logging
from time import localtime, strftime
from nose.plugins.attrib import attr
from collections import Counter
import helpers.db_methods
from helpers.db_methods import *
import csv

from api_objects.factomd_api_objects import FactomApiObjects
from helpers.helpers import read_data_from_json
from api_objects.factom_wallet_api_objects import FactomWalletApiObjects


@attr(entry=True)
class FactomAPIEntryTests(unittest.TestCase):
    '''
    testcases to get all entries and entry size in the blockchain
    '''
    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    factomd_address_prod = data['factomd_address_prod1']
    factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'], data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'], data['factomd_address_6']]
    entrylist_eblock = []
    entrylist_ecblock = []
    chaindict = {}

    def setUp(self):
        self.factom_api = FactomApiObjects()
        self.factom_api_wallet = FactomWalletApiObjects()

    def notest_get_allentries(self):
        self.chaindict=self._fetch_keymr_from_dblock(self.factomd_address_prod)
        self._parse_and_display_chain_details(self.chaindict)

    def _fetch_keymr_from_dblock(self,factomd_address):
        self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        #for i in range(58750, height['entryblockheight']):
        for i in range(58750,58800):
            logging.getLogger('api_command').info("Height = %s" %i)
            print strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
            print "height = %d" %i
            dblock_keymr = self.factom_api.get_directory_block_by_height(i)
            dblock =self.factom_api.get_directory_block_by_keymr(dblock_keymr['keymr'])
            if len(dblock) > 3:
                for x in range(3 , len(dblock)):
                    chainid = dblock[x]['chainid']
                    entry_block=self.factom_api.get_entry_block(dblock[x]['keymr'])
                    len_entrylist=len(entry_block['entrylist'])
                    entryhashlist = {}
                    for y in range(0, len_entrylist):
                        entryhash=entry_block['entrylist'][y]['entryhash']
                        output = self.factom_api.get_entry_by_hash(entryhash)
                        size = len(output['content'])
                        entryhashlist[entryhash] = size
                        if chainid in self.chaindict:
                            self.chaindict[chainid].update(entryhashlist)
                        else:
                            self.chaindict[chainid] = entryhashlist
            #print self.chaindict
        return self.chaindict

    def _parse_and_display_chain_details(self,chainiddict):
        for chainid, entryhash in chainiddict.items():
            logging.getLogger('api_command').info("ChainID = %s ===>>  total entries = %s" % (chainid, str(len(entryhash))))
            print chainid + "===>" + str(len(entryhash))
        logging.getLogger('api_command').info("Total Chains in the Blockchain = %s" % str(len(chainiddict)))
        print len(chainiddict)

    def notest_fetch_chains(self):
        factomd_address = self.factomd_address_prod
        self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        for i in range(0, height['entryblockheight']):
            logging.getLogger('api_command').info("Height = %s" % i)
            print strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
            print "height = %d" % i
            chainid = []
            dblock_keymr = self.factom_api.get_directory_block_by_height(i)
            dblock = self.factom_api.get_directory_block_by_keymr(dblock_keymr['keymr'])
            if len(dblock) > 3:
                for x in range(3, len(dblock)):
                    chainid.append(dblock[x]['chainid'])
        logging.getLogger('api_command').info("Length of Chain = %s" %len(chainid))
        logging.getLogger('api_command').info("List of Chains = %s" %chainid)
        print len(chainid)
        print chainid

    def test_fetch_chains_from_db(self):
        factomd_conn = connect_to_db()
        create_table(factomd_conn)
        factomd_address = self.factomd_address_prod
        self.factom_api.change_factomd_address(factomd_address)
        height = self.factom_api.get_heights()
        for i in range(0,25000):
            logging.getLogger('api_command').info("Height = %s" % i)
            print i
            dblock_keymr = self.factom_api.get_directory_block_by_height(i)
            dblock = self.factom_api.get_directory_block_by_keymr(dblock_keymr['keymr'])
            if len(dblock) > 3:
                for x in range(3, len(dblock)):
                    chainid = dblock[x]['chainid']
                    entry_block = self.factom_api.get_entry_block(dblock[x]['keymr'])
                    len_entrylist = len(entry_block['entrylist'])
                    for y in range(0, len_entrylist):
                        entryhash = entry_block['entrylist'][y]['entryhash']
                        output = self.factom_api.get_entry_by_hash(entryhash)
                        size = len(output['content'])
                        insert_to_db(factomd_conn,entryhash,chainid,size)
                        if i == 1000:
                            commit_to_db(factomd_conn)
        cur = factomd_conn.cursor()
        fetch_from_db(cur)
        chainidlist = cur.fetchall()
        print chainidlist
        print len(chainidlist)
        logging.getLogger('api_command').info("Chain ID = %s" %(chainidlist))
        logging.getLogger('api_command').info("Length of Chain = %s" % len(chainidlist))
        close_connection_to_db(factomd_conn)


    def notest_fetch_data_and_write_to_csv(self):
        csvWriter = csv.writer(open("output.csv", "w"))
        conn = connect_to_db()
        cur = conn.cursor()
        fetch_from_db(cur)
        rows = cur.fetchall()
        csvWriter.writerows(rows)
        close_connection_to_db(conn)