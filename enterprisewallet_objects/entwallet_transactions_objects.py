from helpers.helpers import read_data_from_json
from enterprisewallet_objects.entwallet_objects import EnterpriseWalletObjects

class EnterpriseWalletTransactionsbjects():

    def __init__(self):
        self.entwallet_objects = EnterpriseWalletObjects()
        self.transactions = 'related-transactions'

    def get_transactions_from_enterprise(self):
        result = self.entwallet_objects.send_get_request(self.transactions)
        return result
