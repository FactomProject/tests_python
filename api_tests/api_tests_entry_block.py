from api_objects.factomd_api_objects import FactomApiObjects
import unittest
from helpers.helpers import read_data_from_json
import math

from nose.plugins.attrib import attr
import datetime

@attr(fast=True)
class FactomEntryTests(unittest.TestCase):

    def setUp(self):
        self.factom_api = FactomApiObjects()
        data = read_data_from_json('addresses.json')

        self.factomd_address_prod = data['factomd_windows_laptop']
        #factomd_address_ansible = data['factomd_address']
        #factomd_address_custom_list = [data['factomd_address_0'], data['factomd_address_1'], data['factomd_address_2'],
        #                              data['factomd_address_3'], data['factomd_address_4'], data['factomd_address_5'],
        #                               data['factomd_address_6']]

    def test_get_entries(self):
        delta = []
        self.factom_api.change_factomd_address(self.factomd_address_prod)
        entryhash = "0503fe82359416fc8caecc4a33fbbe94b78f02929e91cbbd022a3c5cab685f6b"
        print "before for loop %s" % str(datetime.datetime.now())
        for j in range(1, 10):
            starttime = datetime.datetime.now()
            print "Iteration %d, time before for loop begins %s" % (j, str(starttime))
            for x in range(1,10):
                str(self.factom_api.get_entry_by_hash(entryhash))
            endtime = datetime.datetime.now()
            print "Iteration %d, time after for loop begins %s" % (j, str(endtime))
            diff = (endtime - starttime).total_seconds()
            delta.append(diff)
            print diff
        print delta
        print "average %f for API test" % (math.fsum(delta)/len(delta))

