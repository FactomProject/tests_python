from api_objects.factomd_api_objects import FactomApiObjects
import unittest
import os

from cli_objects.factom_cli_create import FactomCliCreate
from cli_objects.factom_chain_objects import FactomChainObjects

from helpers.helpers import create_random_string

class FactomChainTests(unittest.TestCase):

    def test_make_chain_with_wrong_address(self):
        factom_api = FactomApiObjects()
        print factom_api.get_directory_block_head()
