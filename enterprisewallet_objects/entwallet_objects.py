import requests
from helpers.helpers import read_data_from_json
import json
import urllib

class EnterpriseWalletObjects():

    def __init__(self):
        data = read_data_from_json('addresses.json')
        enterprisewallet_address = data['enterprisewallet_address']
        self.url_get = 'http://'+ enterprisewallet_address + '/GET?request='
        self.url_post = 'http://'+ enterprisewallet_address + '/POST?request='
        self.url = 'http://'+ enterprisewallet_address + '/POST?'
        

    def send_post_request(self, payload):
        r = requests.post(self.url, params=urllib.urlencode(payload))
        print r.url
        output = json.loads(r.text)
        return output

    def send_get_request(self,request):
        r = requests.get(self.url_get + request)
        output = json.loads(r.text)
        return output