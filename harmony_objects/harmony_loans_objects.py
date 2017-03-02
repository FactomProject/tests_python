import requests
import json

class HarmonyLoansObjects():

    main_address = 'http://localhost:4000'
    loans = '/loans'
    permissions = '/permissions'
    files = '/files'

    def get_all_loans(self, auth_header):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.loans, headers=headers)
        return json.loads(r.text)

    def create_loan(self, auth_header, min, property_address, *borrower):
        headers = {'authorization': auth_header}
        borrowers_list = list(borrower)
        payload = {'min': min, "property_address": property_address, "borrowers": borrowers_list}
        r = requests.post(self.main_address + self.loans, json=payload, headers=headers)
        return json.loads(r.text)

    def get_loan_data(self, auth_header, loan_id):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.loans + '/' + loan_id, headers=headers)
        return json.loads(r.text)

    def update_loan_address_put(self,  auth_header, loan_id, property_address):
        headers = {'authorization': auth_header}
        payload = {"property_address": property_address}
        r = requests.put(self.main_address + self.loans + '/' + loan_id, json=payload, headers=headers)
        return json.loads(r.text)

    def list_loan_permissions(self, auth_header, loan_id):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.loans + '/' + loan_id + self.permissions, headers=headers)
        return json.loads(r.text)

    def create_new_loan_permission(self, auth_header, loan_id, user_id, access_from_date, access_to_date):
        headers = {'authorization': auth_header}
        payload = {"user_id": user_id, "access_from": access_from_date, "access_to": access_to_date}
        r = requests.post(self.main_address + self.loans + '/' + loan_id + self.permissions, json=payload, headers=headers)
        return json.loads(r.text)

    def list_loan_files(self, auth_header, loan_id):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.loans + '/' + loan_id + self.files, headers=headers)
        return json.loads(r.text)

    def get_loan_file_data(self, auth_header, loan_id, files_id):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.loans + '/' + loan_id + self.files + '/' + files_id, headers=headers)
        return json.loads(r.text)

    def update_loan_permission_end_date(self, auth_header, loan_id, permission_id, permission_end_date):
        headers = {'authorization': auth_header}
        payload = {"access_to": permission_end_date}
        r = requests.put(self.main_address + self.loans + '/' + loan_id + self.permissions + '/' + permission_id, json=payload, headers=headers)
        return json.loads(r.text)

    def create_new_loan_file(self, auth_header, loan_id, document_data):
        '''
        Creates new loan file
        :param loan_id: str - load id
        :param document_data: json with fields: storage id, document_id, type, name, document_date, version, source,
         location_name, location path, archived(bool)
        :return: api response
        '''
        payload = document_data
        headers = {'authorization': auth_header}
        r = requests.post(self.main_address + self.loans + '/' + loan_id + self.files, json=payload, headers=headers)
        return json.loads(r.text)

    def update_loan_file_data(self, auth_header, loan_id, document_data):
        headers = {'authorization': auth_header}
        payload = document_data
        r = requests.put(self.main_address + self.loans + '/' + loan_id + self.files, json=payload, headers=headers)
        return json.loads(r.text)

    def delete_loan_permission_data(self, auth_header, loan_id, permission_id):
        headers = {'authorization': auth_header}
        r = requests.delete(self.main_address + self.loans + '/' + loan_id + self.permissions + '/' + permission_id,
                            headers=headers)





