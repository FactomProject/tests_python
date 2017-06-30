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


@attr(allentry=True)
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
                        insert_to_db(factomd_conn, entryhash, chainid, size)
                        if i % 100 == 0:
                            commit_to_db(factomd_conn)
        cur = factomd_conn.cursor()
        fetch_from_db(cur)
        chainidlist = cur.fetchall()
        print chainidlist
        print len(chainidlist)
        logging.getLogger('api_command').info("Chain ID = %s" % (chainidlist))
        logging.getLogger('api_command').info("Length of Chain = %s" % len(chainidlist))
        close_connection_to_db(factomd_conn)


    def notest_fetch_data_and_write_to_csv(self):
        csvWriter = csv.writer(open("misc-data.csv", "a"))
        conn = connect_to_db()
        cur = conn.cursor()
        fetch_from_db(cur)
        rows = cur.fetchall()
        csvWriter.writerows(rows)
        close_connection_to_db(conn)

    def notest_fetch_entries_from_ecblock(self):
        factomd_conn = connect_to_db()
        create_table_ecblock(factomd_conn)
        self.factom_api.change_factomd_address(self.factomd_address_prod)
        height = self.factom_api.get_heights()
        for i in range(35000,45000):
            ecblock = self.factom_api.get_entry_credit_block_by_height(i)
            len_entries = len(ecblock['body']['entries'])
            logging.getLogger('api_command').info("Height = %s" % i)
            #check for entries more than 10 because there are 0 to 9 minute markers
            if len_entries > 10:
                for x in range(0, len_entries):
                    entries = ecblock['body']['entries'][x]
                    if 'entryhash' in entries:
                        entryhash = ecblock['body']['entries'][x]['entryhash']
                        credits = ecblock['body']['entries'][x]['credits']
                        insert_to_ecblock(factomd_conn,entryhash,credits,i)
                        if i % 100 == 0:
                            commit_to_db(factomd_conn)
        cur = factomd_conn.cursor()
        fetch_from_ecblock_db(cur)
        entryhashlist = cur.fetchall()
        logging.getLogger('api_command').info("EntryHash list = %s" % (entryhashlist))
        logging.getLogger('api_command').info("Total EntryHash = %s" % len(entryhashlist))
        close_connection_to_db(factomd_conn)