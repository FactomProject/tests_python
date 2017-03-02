import unittest
import json

from helpers.helpers import create_random_number, read_data_from_json, create_random_string
from nose.plugins.attrib import attr

from harmony_objects.harmony_loans_objects import HarmonyLoansObjects
from harmony_objects.harmony_users_objects import HarmonyUsersObjects
from harmony_objects.harmony_storage_and_misc_objects import HarmonyStorageMiscObjects

@attr(harmony=True)
class FactomChainTests(unittest.TestCase):
    data = read_data_from_json('harmony_test_data.json')
    user_data = read_data_from_json('harmony_user_data.json')

    def setUp(self):
        self.loans_api = HarmonyLoansObjects()
        self.users_api = HarmonyUsersObjects()
        self.storage_and_misc_api = HarmonyStorageMiscObjects()

    def test_all_loans(self):
        header = self._login_as_user_and_receive_header()
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        self.loans_api.create_loan(header, str(number), address, first_name, second_name)

        loans_list = self.loans_api.get_all_loans(header)
        self.assertTrue(len(loans_list) > 0)

    def test_post_loan(self):
        header = self._login_as_user_and_receive_header()
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.loans_api.create_loan(header, str(number), address, first_name, second_name)
        self.assertTrue(loan['min'] == str(number), 'Correct min is not created')
        self.assertTrue(bool(loan['id'] and loan['id'].strip()))

    def test_get_loan_data(self):
        header = self._login_as_user_and_receive_header()
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.loans_api.create_loan(header, str(number), address, first_name, second_name)
        loan_id = loan['id']
        loan_received = self.loans_api.get_loan_data(header, loan_id)
        self.assertTrue(address == loan_received["property_address"])
        self.assertTrue(str(number) == loan_received["min"])
        self.assertTrue(first_name in loan_received["borrowers"] and second_name in loan_received["borrowers"])
        self.assertTrue(loan_id == loan_received['id'])

    def test_update_loan(self):
        header = self._login_as_user_and_receive_header()
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.loans_api.create_loan(header, str(number), address, first_name, second_name)
        loan_id = loan['id']
        address_2 = create_random_string(10)
        response_loan = self.loans_api.update_loan_address_put(header, loan_id, address_2)
        self.assertTrue(address_2 == response_loan["property_address"])
        loan_received = self.loans_api.get_loan_data(header, loan_id)
        self.assertTrue(address_2 == loan_received["property_address"])

    def test_create_loan_permission_and_list_all_loan_permissions(self):
        header = self._login_as_user_and_receive_header()
        loan_id = self._create_loan_and_receive_id(header)
        #user cration
        user_name = create_random_string(10)
        user_email = user_name + '@example.com'
        user_data = self.user_data['user1']
        user_data['username'] = user_name
        user_data['email'] = user_email
        user = self.users_api.create_new_user(header, user_data)

        user_id = user['id']

        self.assertTrue(user_id == self.loans_api.create_new_loan_permission(header, loan_id, user_id,
                                                                             self.data['permission_start_date'],
                                                                             self.data['permission_end_date'])['user_id'])

        loan_permissions_list = self.loans_api.list_loan_permissions(header, loan_id)
        self.assertTrue(len(loan_permissions_list) > 0)

    def test_create_loan_permission_with_wrong_date(self):
        header = self._login_as_user_and_receive_header()
        loan_id = self._create_loan_and_receive_id(header)
        # user cration
        user_name = create_random_string(10)
        user_email = user_name + '@example.com'
        user_data = self.user_data['user1']
        user_data['username'] = user_name
        user_data['email'] = user_email
        user = self.users_api.create_new_user(header, user_data)

        user_id = user['id']
        #date starts before ends
        self.assertTrue('should be before access_to' in
                        json.dumps(self.loans_api.create_new_loan_permission(header, loan_id, user_id,
                                                                             self.data['permission_end_date'],
                                                                             self.data['permission_start_date'])
                                   ['errors']['access_from']))

        #dates are same
        self.assertTrue('should be before access_to' in
                        json.dumps(self.loans_api.create_new_loan_permission(header, loan_id, user_id,
                                                                             self.data['permission_start_date'],
                                                                             self.data['permission_start_date'])
                                   ['errors']['access_from']))

        #dates are wrong
        self.assertTrue('is invalid' in json.dumps(self.loans_api.create_new_loan_permission(header, loan_id, user_id,'text',
                                                                                             'text')['errors']
                                                   ['access_from']))

    def test_update_load_permission_data(self):
        header = self.storage_and_misc_api.login_as_user("joel", "joel")
        loan_id = self._create_loan_and_receive_id(header)
        # user cration
        user_name = create_random_string(10)
        user_email = user_name + '@example.com'
        user_data = self.user_data['user1']
        user_data['username'] = user_name
        user_data['email'] = user_email
        user = self.users_api.create_new_user(header, user_data)

        user_id = user['id']
        new_end_data = self.data['permission_end_date2']

        perm = self.loans_api.create_new_loan_permission(header, loan_id, user_id, self.data['permission_start_date'], self.data['permission_end_date'])
        perm_id = perm['id']
        perm_after = self.loans_api.update_loan_permission_end_date(header, loan_id, perm_id, new_end_data)
        self.assertTrue(new_end_data == perm_after['access_to'])

    def test_delete_permission(self):
        header = self.storage_and_misc_api.login_as_user("joel", "joel")
        loan_id = self._create_loan_and_receive_id(header)
        # user cration
        user_name = create_random_string(10)
        user_email = user_name + '@example.com'
        user_data = self.user_data['user1']
        user_data['username'] = user_name
        user_data['email'] = user_email
        user = self.users_api.create_new_user(header, user_data)

        user_id = user['id']
        new_end_data = self.data['permission_end_date2']

        perm = self.loans_api.create_new_loan_permission(header, loan_id, user_id, self.data['permission_start_date'],
                                                         self.data['permission_end_date'])
        perm_id = perm['id']



    def _login_as_user_and_receive_header(self):
        return self.storage_and_misc_api.login_as_user("joel", "joel")

    def _create_loan_and_receive_id(self, header):
        number = create_random_number(18)
        first_name = self.data['name_1']
        second_name = self.data['name_2']
        address = self.data['address']
        loan = self.loans_api.create_loan(header, str(number), address, first_name, second_name)
        return loan['id']




