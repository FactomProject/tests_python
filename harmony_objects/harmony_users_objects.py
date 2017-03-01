import requests
import json

class HarmonyUsersObjects():

    main_address = 'http://localhost:4000'
    users = '/users'
    reset = '/passwordr_reset' #not ready, use when auth created

    def list_all_users(self):
        r = requests.get(self.main_address + self.users)
        return json.loads(r.text)

    def get_user_data(self, user_id):
        r = requests.get(self.main_address + self.users + '/' + user_id)
        return json.loads(r.text)

    def create_new_user(self, user_data_json):
        payload = user_data_json
        r = requests.post(self.main_address + self.users, json=payload)
        return json.loads(r.text)

    def update_user_data(self, user_id, user_data_json):
        payload = user_data_json
        r = requests.put(self.main_address + self.users + '/' + user_id, json=payload)
        return json.loads(r.text)


