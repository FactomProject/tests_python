
class PostTransactionObjects():

    def __init__(self):

        self.transtype = ""
        self.outputaddresses = []
        self.outputamounts = ""
        self.inputaddresses = []
        self.inputamounts = []
        self.feeaddress = ""
        self.signature = ""
        self.inputstring = ""

    def print_values(self):
        print self.transtype
        print self.outputaddresses
        print self.outputamounts

    def make_inputparameter(self):
        if self.transtype == "factoid" or self.transtype == "ec":
            self.inputstring = '{"TransType":"'+ self.transtype + '","OutputAddresses":["' + self.outputaddresses + '"],"OutputAmounts":["' + str(
                       self.outputamounts) + '"]}'
        elif self.transtype == "custom":
            self.inputstring = '{"TransType":"'+ self.transtype + '","OutputAddresses":["' + self.outputaddresses + '"],"OutputAmounts":["' + str(
                            self.outputamounts) + '"],"InputAddresses":["' + self.inputaddresses + '"],"InputAmounts":["' + str(self.inputamounts) + '"],"FeeAddress":"' + self.feeaddress + '"}'
        else:
            self.inputstring = '{"TransType":"'+ self.transtype + '","OutputAddresses":["' + self.outputaddresses + '"],"OutputAmounts":["' + str(
                                 self.outputamounts) + '"],"InputAddresses":["' + self.inputaddresses + '"],"InputAmounts":["' + str(self.inputamounts) + '"],"FeeAddress":"' + self.feeaddress + '","Signature":"' + self.signature + '"}'

        return self.inputstring
