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
class APITestsLoadNodes(unittest.TestCase):
    api_factomd = APIObjectsFactomd()
    api_wallet = APIObjectsWallet()
    cli_chain = CLIObjectsChain()
    cli_create = CLIObjectsCreate()
    blocktime = api_factomd.get_current_minute()['directoryblockinseconds']
    data = read_data_from_json('shared_test_data.json')


    def setUp(self):
        self.first_address = self.cli_create.import_addresses(self.data['factoid_wallet_address'])[0]
        self.ecrate = self.cli_create.get_entry_credit_rate()
        #print self.entry_credit_address1000000
        self.entry_credit_address1000000 = self.cli_create.create_entry_credit_address()
        timestr = time.strftime("%Y%m%d-%H%M%S")
        logging.basicConfig(filename="perf_" + timestr + "_.txt", level=logging.INFO,format='%(asctime)s %(message)s')

    def test_chain_entry_for_loadtesting(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        f = open("performance_" + str(timestr) + ".txt","w")

        for i in range(5):
            chain_external_ids, content = generate_random_external_ids_and_content()

            # compose chain
            compose = self.api_wallet.compose_chain(chain_external_ids, content, self.entry_credit_address1000000)

            # commit chain
            commit = self.api_factomd.commit_chain(compose['commit']['params']['message'])

            # reveal_chain
            reveal = self.api_factomd.reveal_chain(compose['reveal']['params']['entry'])
            chainid = reveal['chainid']
            print chainid

            logging.info("Chain_Created " + reveal['chainid'])
            #f.write(str(datetime.datetime.now()) +" Chain_Created " + reveal['chainid'] + "\n")

            chain_external_ids.insert(0, '-h')
            chain_external_ids.insert(2, '-h')

            status = wait_for_chain_in_block(external_id_list=chain_external_ids)
            #if status contains chainid then, print the time stamp
            result = re.search(chainid,status).group(0)
            logging.info("Chain_Acknowledged " + result)
            #f.write(str(datetime.datetime.now()) + " Chain_Acknowledged " + result + "\n")


            total_entries = 20001
            for i in range(0, total_entries):
                # compose entry

                #chain_id = "e5c2d457bd682157f27f66e5c818b83c464e430e3564388fcdbed94debbd9442"
                entry_external_ids, content = generate_random_external_ids_and_content()
                compose = self.api_wallet.compose_entry(chainid, entry_external_ids, content,
                                                self.entry_credit_address1000000)

                # commit entry
                commit = self.api_factomd.commit_entry(compose['commit']['params']['message'])

                # reveal entry
                reveal = self.api_factomd.reveal_entry(compose['reveal']['params']['entry'])
                entry_hash = reveal['entryhash']
                print entry_hash


                #time.sleep(0.25)

                # entry arrived in block?
                val = (i % 1000)
                if val == 0:
                    #print i
                    logging.info(str(i) + "th before Acknowledgement " + result)
                    f.write(str(datetime.datetime.now()) + " " + str(i) + "th before Acknowledgement " + result + "\n")
                    self.entry_credit_address1000000 = fund_entry_credit_address(1000000)
                    status = wait_for_entry_in_block(reveal['entryhash'], reveal['chainid'])
                    result = re.search(entry_hash,status).group(0)
                    logging.info(str(i) + "th Entry_Acknowledged " + result)
                    f.write(str(datetime.datetime.now()) + " " + str(i) + "th Entry_Acknowledged " + result + "\n")
                    #time.sleep(30)
            #time.sleep(30)

        f.close()



