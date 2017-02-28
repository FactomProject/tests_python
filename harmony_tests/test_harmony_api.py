import unittest
from helpers.helpers import create_random_number, read_data_from_json, create_random_string

from nose.plugins.attrib import attr

from harmony_objects.harmony_loans_objects import HarmonyLoansObjects

@attr(fast=True)
class FactomChainTests(unittest.TestCase):
    data = read_data_from_json('harmony_test_data.json')
    def setUp(self):
        self.harmony_api = HarmonyLoansObjects()



    def test_all_loans(self):
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        self.harmony_api.create_loan(str(number), address, first_name, second_name)

        loans_list = self.harmony_api.get_all_loans()
        self.assertTrue(len(loans_list) > 0)

    def test_post_loan(self):
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.harmony_api.create_loan(str(number), address, first_name, second_name)
        self.assertTrue(loan['min'] == str(number), 'Correct min is not created')
        self.assertTrue(bool(loan['id'] and loan['id'].strip()))

    def test_get_loan_data(self):
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.harmony_api.create_loan(str(number), address, first_name, second_name)
        loan_id = loan['id']
        loan_received = self.harmony_api.get_loan_data(loan_id)
        self.assertTrue(address == loan_received["property_address"])
        self.assertTrue(str(number) == loan_received["min"])
        self.assertTrue(first_name in loan_received["borrowers"] and second_name in loan_received["borrowers"])
        self.assertTrue(loan_id == loan_received['id'])

    def test_update_loan(self):
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.harmony_api.create_loan(str(number), address, first_name, second_name)
        loan_id = loan['id']
        address_2 = create_random_string(10)
        response_loan = self.harmony_api.update_loan_address_put(loan_id, address_2)
        self.assertTrue(address_2 == response_loan["property_address"])
        loan_received = self.harmony_api.get_loan_data(loan_id)
        self.assertTrue(address_2 == loan_received["property_address"])

    def test_list_loan_permissions(self):
        loan_id = self._create_loan_and_receive_id()
        self.harmony_api.list_loan_permissions(loan_id)

    def test_create_loan_permission(self):
        #Todo - after creating users
        loan_id = self._create_loan_and_receive_id()
        print self.harmony_api.create_new_loan_permission(loan_id, 'test', '2017-01-01T12:00:00Z', '2017-03-01T12:00:00Z')


    def _create_loan_and_receive_id(self):
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.harmony_api.create_loan(str(number), address, first_name, second_name)
        return loan['id']




