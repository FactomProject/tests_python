import unittest, time

from nose.plugins.attrib import attr
from api_objects.api_objects_factomd import APIObjectsFactomd
from api_objects.api_objects_wallet import APIObjectsWallet

from cli_objects.cli_objects_chain import CLIObjectsChain
from cli_objects.cli_objects_create import CLIObjectsCreate
from helpers.helpers import create_random_string, read_data_from_json
from helpers.general_test_methods import fund_entry_credit_address, wait_for_chain_in_block, wait_for_entry_in_block
from helpers.api_methods import generate_random_external_ids_and_content

from random import randint

import logging
import time
import re
import datetime


@attr(load=True)
class CLITestsLoadNodes(unittest.TestCase):
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('shared_test_data.json')


    def setUp(self):
        self.first_address = self.cli_create.import_addresses(self.data['factoid_wallet_address'])[0]
        self.ecrate = self.cli_create.get_entry_credit_rate()
        self.entry_credit_address1000000 = fund_entry_credit_address(1000000)
        #print self.entry_credit_address1000000
        #self.entry_credit_address1000 = fund_entry_credit_address(1000)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        logging.basicConfig(filename="perf_" + timestr + "_.txt", level=logging.INFO,format='%(asctime)s %(message)s')

    def test_make_chain_and_check_balance(self):
        '''
        ENTRIES in block is defined in shared_test_data.json,
        blocktime is value passed to docker container at start
        increasing ENTRIES_PER_BLOCK decreases sleep time between entries.
        set CONTINUOUS for no sleeping at all.
        '''
        # CONTINUOUS = True

        # print statement is necessary to see the calculated sleep time
        print 'sleep time', float(self.blocktime) / float(self.data['ENTRIES_PER_BLOCK'])
        self.cli_create.check_wallet_address_balance(self.entry_credit_address1000000)
        chain_flags_list = ['-f', '-C']
        for i in xrange(20):
            for i in range(80):
                name_1 = create_random_string(5)
                name_2 = create_random_string(5)
                names_list = ['-n', name_1, '-n', name_2]
                content = create_random_string(randint(100, 5000))
                chain_id = self.cli_chain.make_chain(self.entry_credit_address1000000, content, external_id_list=names_list, flag_list=chain_flags_list)
                #print chain_id
                #wait_for_chain_in_block(external_id_list=names_list)

                for i in range(120):
                    name_1 = create_random_string(5)
                    name_2 = create_random_string(5)
                    names_list = ['-c', chain_id, '-e', name_1, '-e', name_2]
                    content = create_random_string(randint(100, 5000))
                    entry_hash = self.cli_chain.add_entry_to_chain(self.entry_credit_address1000000, content, external_id_list=names_list, flag_list=chain_flags_list)

                   # if not CONTINUOUS: time.sleep(float(self.blocktime) / float(self.data['ENTRIES_PER_BLOCK']) * 0.2)
                    self.assertFalse('0' == self.cli_create.check_wallet_address_balance(self.entry_credit_address1000000), 'out of entry credits')
                    wait_for_entry_in_block(entry_hash, chain_id)


    def test_chain_entry_thru_api(self):
        for i in range(1):
            chain_external_ids, content = generate_random_external_ids_and_content()

            # compose chain
            compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000000)

            # commit chain
            commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

            # reveal_chain
            reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])
            chainid = reveal['chainid']

            logging.info("Chain_Created " + reveal['chainid'])

            chain_external_ids.insert(0, '-h')
            chain_external_ids.insert(2, '-h')

            status = wait_for_chain_in_block(external_id_list=chain_external_ids)
            #if status contains chainid then, print the time stamp
            result = re.search(chainid,status).group(0)
            logging.info("Chain_Acknowledged " + result)

            total_entries = 20001

            for i in range(0, total_entries):
                # compose entry

                entry_external_ids, content = generate_random_external_ids_and_content()
                compose = self.api_wallet.compose_entry(reveal['chainid'], entry_external_ids, content,
                                                self.entry_credit_address1000000)

                # commit entry
                commit = self.api_factomd.commit_entry(compose['commit']['params']['message'])

                # reveal entry
                reveal = self.api_factomd.reveal_entry(compose['reveal']['params']['entry'])
                entry_hash = reveal['entryhash']

                #time.sleep(1)

                # entry arrived in block?
                val = (i % 1000)
                if val == 0:
                    print i
                    status = wait_for_entry_in_block(reveal['entryhash'], reveal['chainid'])
                    result = re.search(entry_hash,status).group(0)
                    logging.info(str(i) + "th Entry_Acknowledged " + result)
                    #time.sleep(30)
            #time.sleep(30)

    def test_chain_entry_for_loadtesting(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        f = open("performance_" + str(timestr) + ".txt","w")

        for i in range(1):
            chain_external_ids, content = generate_random_external_ids_and_content()

            # compose chain
            compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000000)

            # commit chain
            commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

            # reveal_chain
            reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])
            chainid = reveal['chainid']

            logging.info("Chain_Created " + reveal['chainid'])
            f.write(str(datetime.datetime.now()) +" Chain_Created " + reveal['chainid'])

            chain_external_ids.insert(0, '-h')
            chain_external_ids.insert(2, '-h')

            status = wait_for_chain_in_block(external_id_list=chain_external_ids)
            #if status contains chainid then, print the time stamp
            result = re.search(chainid,status).group(0)
            logging.info("Chain_Acknowledged " + result)
            f.write(str(datetime.datetime.now()) + " Chain_Acknowledged " + result)

            total_entries = 20001

            for i in range(0, total_entries):
                # compose entry

                entry_external_ids, content = generate_random_external_ids_and_content()
                compose = self.api_wallet.compose_entry(reveal['chainid'], entry_external_ids, content,
                                                self.entry_credit_address1000000)

                # commit entry
                commit = self.api_factomd.commit_entry(compose['commit']['params']['message'])

                # reveal entry
                reveal = self.api_factomd.reveal_entry(compose['reveal']['params']['entry'])
                entry_hash = reveal['entryhash']

                #time.sleep(1)

                # entry arrived in block?
                val = (i % 1000)
                if val == 0:
                    print i
                    status = wait_for_entry_in_block(reveal['entryhash'], reveal['chainid'])
                    result = re.search(entry_hash,status).group(0)
                    logging.info(str(i) + "th Entry_Acknowledged " + result)
                    f.write(str(datetime.datetime.now()) + " " + str(i) + "th Entry_Acknowledged " + result)
                    #time.sleep(30)
            #time.sleep(30)
        f.close()

