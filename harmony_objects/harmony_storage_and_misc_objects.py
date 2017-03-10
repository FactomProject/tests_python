import requests
import json

class HarmonyStorageMiscObjects():

    main_address = 'https://harmony-api-dev.factom.com'
    storage = '/storage'
    doc_types = '/doc_types'
    sessions = '/sessions'


    def get_document_from_storage(self, id):
        r = requests.get(self.main_address + self.storage + '/' + id)
        return json.loads(r.text) #todo save and load binary

    def upload_document_to_storage(self, file_path, filename):
        payload={'file': filename}
        files = {filename: open(file_path, 'rb')}
        r =requests.post(self.main_address + self.storage, json=payload, files=files)
        return json.loads(r.text)

    def get_all_doc_types(self):
        r = requests.get(self.main_address + self.doc_types)
        return json.loads(r.text)

    def get_doc_type_by_id(self, doc_id):
        r = requests.get(self.main_address + self.doc_types + '/' + doc_id)
        return json.loads(r.text)

    def login_as_user(self, username, password):
        payload = {"username": username, "password": password}
        r = requests.post(self.main_address + self.sessions, json=payload)
        return r.headers['authorization']

