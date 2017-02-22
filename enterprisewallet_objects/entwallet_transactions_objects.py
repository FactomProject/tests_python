from helpers.helpers import read_data_from_json
from enterprisewallet_objects.entwallet_objects import EnterpriseWalletObjects


class EnterpriseWalletTransactionsbjects():

    def __init__(self):
        self.entwallet_objects = EnterpriseWalletObjects()
        self.transactions = 'related-transactions'
        self.maketransactions = 'make-transaction'
        self.sendtransactions = 'send-transaction'


    def get_transactions_from_enterprisewallet(self):
        result = self.entwallet_objects.send_get_request(self.transactions)
        return result

    def make_transactions_on_enterprisewallet(self,inputstring):
         payload = (('request',self.maketransactions),('json', inputstring))
         result = self.entwallet_objects.send_post_request(payload)
         return result

    def send_transactions_on_enterprisewallet(self,inputstring):
         payload = (('request', self.sendtransactions),('json', inputstring))
         result = self.entwallet_objects.send_post_request(payload)
         return result






