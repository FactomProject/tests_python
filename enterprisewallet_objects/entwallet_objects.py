import requests
from helpers.helpers import read_data_from_json
import json

class EnterpriseWalletObjects():

    def __init__(self):
        data = read_data_from_json('addresses.json')
        enterprisewallet_address = data['enterprisewallet_address']
        self.url_get = 'http://'+ enterprisewallet_address + '/GET?request='
        self.url_post = 'http://'+ enterprisewallet_address + '/POST?request='
        self.url = 'http://'+ enterprisewallet_address + '/POST'

    def send_post_request_new(self, payload):
        #r = requests.post(self.url_post + request + "&json=" + payload)
        r = requests.get(self.url, params=payload)
        print self.url + str(payload)
        #output = json.loads(r.text)
        return r.text

    def send_post_request(self,request, payload):
        r = requests.post(self.url_post + request + "&json=" + payload)
        #r = requests.post(self.url)
        #print self.url_post + request + "&json=" + payload
        output = json.loads(r.text)
        return output

    def send_get_request(self,request):
        r = requests.get(self.url_get + request)
        output = json.loads(r.text)
        return output