from apiplus_objects.apiplus_objects import ApiplusApiObjects
import unittest
import time

from helpers.helpers import create_random_string

from nose.plugins.attrib import attr

@attr(apiplus=True)
class FactomChainTests(unittest.TestCase):
    BLOCKCHAIN_TIME = 120

    def setUp(self):
        self.apiplus_api = ApiplusApiObjects()

    def test_chain_creation(self):
        chain_id = self._create_chain_and_receive_id()
        time.sleep(self.BLOCKCHAIN_TIME)
        list = self.apiplus_api.get_list_of_chains()
        self.assertTrue(chain_id == list['items'][len(list['items']) -1]['chain_id'])

    def test_get_chain_list(self):
        chains = self.apiplus_api.get_list_of_chains()
        self.assertTrue(len(chains['items']) > 0)

    def test_get_chain_by_chain_id(self):
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        content = create_random_string(10)
        chain = self.apiplus_api.create_new_chain(content, name_1, name_2)
        chain_id = chain['chain_id']
        time.sleep(self.BLOCKCHAIN_TIME)
        received_chain = self.apiplus_api.get_chain_by_chainid(chain_id)
        self.assertTrue(chain_id == received_chain['chain_id'], 'Wrong chain id after creation')
        self.assertTrue(name_1 in received_chain['external_ids'] and name_2 in received_chain['external_ids'],
                        'Missing ids in chains')

    def test_create_entry_in_chain(self):
        chain_id = self._create_chain_and_receive_id()
        time.sleep(self.BLOCKCHAIN_TIME)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        content = create_random_string(10)
        entry = self.apiplus_api.create_entry_in_chain(chain_id, content, name_1, name_2)
        self.assertTrue(entry['entry_id'])

    def test_get_first_chain_entry(self):
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        content = create_random_string(10)
        chain = self.apiplus_api.create_new_chain(content, name_1, name_2)
        chain_id = chain['chain_id']
        time.sleep(self.BLOCKCHAIN_TIME)
        entry = self.apiplus_api.get_first_chain_entry(chain_id)
        self.assertTrue(content == entry['content'])

    def test_get_last_chain_entry(self):
        chain_id = self._create_chain_and_receive_id()
        time.sleep(self.BLOCKCHAIN_TIME)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        content = create_random_string(10)
        self.apiplus_api.create_entry_in_chain(chain_id, content, name_1, name_2)
        time.sleep(self.BLOCKCHAIN_TIME)
        last_entry = self.apiplus_api.get_last_chain_entry(chain_id)
        self.assertTrue(content == last_entry['content'])

    def test_get_specific_entry_from_chain(self):
        chain_id = self._create_chain_and_receive_id()
        time.sleep(self.BLOCKCHAIN_TIME)
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        content = create_random_string(10)
        entry = self.apiplus_api.create_entry_in_chain(chain_id, content, name_1, name_2)
        entry_id = entry['entry_id']
        time.sleep(self.BLOCKCHAIN_TIME)
        specific_entry = self.apiplus_api.get_entry_by_chain_id_and_entry_id(chain_id, entry_id)
        self.assertTrue(chain_id == specific_entry['chain_id'], 'Wrong entry id after receiving entry')
        self.assertTrue(entry_id == specific_entry['entry_id'], 'Wrong entry id after receiving entry')
        self.assertTrue(name_1 in specific_entry['external_ids'] and name_2 in specific_entry['external_ids'],
                        'Wrong external ids')
        self.assertTrue(content == specific_entry['content'], 'Wrong content in entry')

    def _create_chain_and_receive_id(self):
        name_1 = create_random_string(5)
        name_2 = create_random_string(5)
        content = create_random_string(10)
        chain = self.apiplus_api.create_new_chain(content, name_1, name_2)
        return chain['chain_id']


