import requests
import json

class HarmonyUsersObjects():

    main_address = 'https://harmony-api-dev.factom.com'
    users = '/users'
    reset = '/passwordr_reset' #not ready, use when auth created

    def list_all_users(self, auth_header):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.users, headers=headers)
        return json.loads(r.text)

    def get_user_data(self, auth_header, user_id):
        headers = {'authorization': auth_header}
        r = requests.get(self.main_address + self.users + '/' + user_id, headers=headers)
        return json.loads(r.text)

    def create_new_user(self, auth_header, user_data_json):
        headers = {'authorization': auth_header}
        payload = user_data_json
        r = requests.post(self.main_address + self.users, json=payload, headers=headers)
        return json.loads(r.text)

    def update_user_data(self, auth_header, user_id, user_data_json):
        headers = {'authorization': auth_header}
        payload = user_data_json
        r = requests.put(self.main_address + self.users + '/' + user_id, json=payload, headers=headers)
        return json.loads(r.text)


