import requests
import json

class HarmonyLoansObjects():

    main_address = 'http://localhost:4000'
    loans = '/loans'
    permissions = '/permissions'
    files = '/files'


    def get_all_loans(self):
        r = requests.get(self.main_address + self.loans)
        return json.loads(r.text)

    def create_loan(self, min, property_address, *borrower):
        borrowers_list = list(borrower)
        payload = {'min': min, "property_address": property_address, "borrowers": borrowers_list}
        r = requests.post(self.main_address + self.loans, json=payload)
        return json.loads(r.text)

    def get_loan_data(self, loan_id):
        r = requests.get(self.main_address + self.loans + '/' + loan_id)
        return json.loads(r.text)

    def update_loan_address_put(self, loan_id, property_address):
        payload = {"property_address": property_address}
        r = requests.put(self.main_address + self.loans + '/' + loan_id, json=payload)
        return json.loads(r.text)

    def list_loan_permissions(self, loan_id):
        r = requests.get(self.main_address + self.loans + '/' + loan_id + self.permissions)
        return json.loads(r.text)

    def create_new_loan_permission(self, loan_id, user_id, access_from_date, access_to_date):
        payload = {"user_id": user_id, "access_from": access_from_date, "access_to": access_to_date}
        r = requests.post(self.main_address + self.loans + '/' + loan_id + self.permissions, json=payload)
        return json.loads(r.text)

    def list_loan_files(self, loan_id):
        r = requests.get(self.main_address + self.loans + '/' + loan_id + self.files)
        return json.loads(r.text)

    def get_loan_file_data(self, loan_id, files_id):
        r = requests.get(self.main_address + self.loans + '/' + loan_id + self.files + '/' + files_id)
        return json.loads(r.text)

    def update_loan_permission_end_date(self, loan_id, permission_id, permission_end_date):
        payload = {"access_to": permission_end_date}
        r = requests.put(self.main_address + self.loans + '/' + loan_id + self.permissions + '/' + permission_id, json=payload)
        return json.loads(r.text)

    def create_new_loan_file(self, loan_id, document_data):
        '''
        Creates new loan file
        :param loan_id: str - load id
        :param document_data: json with fields: storage id, document_id, type, name, document_date, version, source,
         location_name, location path, archived(bool)
        :return: api response
        '''
        payload = document_data
        r = requests.post(self.main_address + self.loans + '/' + loan_id + self.files, json=payload)
        return json.loads(r.text)

    def update_loan_file_data(self, loan_id, document_data):
        payload = document_data
        r = requests.put(self.main_address + self.loans + '/' + loan_id + self.files, json=payload)
        return json.loads(r.text)





