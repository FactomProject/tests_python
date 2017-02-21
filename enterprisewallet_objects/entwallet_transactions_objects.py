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

    def make_factoid_transactions_on_enterprisewallet(self,outputaddress,outputamount):
         payload = (('request', self.maketransactions),
                    ('json', '{"TransType":"factoid","OutputAddresses":["' + outputaddress + '"],"OutputAmounts":["' + str(outputamount) + '"]}'))
         result = self.entwallet_objects.send_post_request(payload)
         return result

    def send_factoid_transactions_on_enterprisewallet(self,outputaddress,outputamount):
         payload = (('request', self.sendtransactions),
                    ('json', '{"TransType":"factoid","OutputAddresses":["' + outputaddress + '"],"OutputAmounts":["' + str(outputamount) + '"]}'))
         result = self.entwallet_objects.send_post_request(payload)
         return result

    def make_ec_transactions_on_enterprisewallet(self,outputaddress,outputamount):
        payload = (('request', self.maketransactions),
                   ('json',
                    '{"TransType":"ec","OutputAddresses":["' + outputaddress + '"],"OutputAmounts":["' + str(
                        outputamount) + '"]}'))
        result = self.entwallet_objects.send_post_request(payload)
        return result

    def send_ec_transactions_on_enterprisewallet(self,outputaddress,outputamount):
         payload = (('request', self.sendtransactions),
                    ('json', '{"TransType":"ec","OutputAddresses":["' + outputaddress + '"],"OutputAmounts":["' + str(outputamount) + '"]}'))
         result = self.entwallet_objects.send_post_request(payload)
         return result
