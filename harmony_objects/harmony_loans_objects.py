import requests
import json

class HarmonyLoansObjects():

    main_address = 'http://localhost:4000'
    loans = '/loans'
    permissions = '/permissions'


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








