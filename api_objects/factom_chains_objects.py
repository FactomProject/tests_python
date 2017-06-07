# Write Factom Entry API

# This software shows how to write data to an already created chain with the Factom API in Python

# This software is MIT licensed, Copyright 2015 Factom Foundation.

# sudo apt-get install python-pip
# sudo apt-get install python-dev
# sudo pip install ed25519
# sudo pip install base58

# factomd should be running on the local computer
import requests
import json

from helpers.helpers import read_data_from_json
import requests
import json
import time
import ed25519
import base58
import hashlib
import struct


class FactomApiChainObjects():

    data = read_data_from_json('addresses.json')
    factomd_address = data['factomd_address']
    # replace this private key with a 32 byte hex string which is random
    # run the code to find the Entry Credit address to buy credits for
    privateECKey = "0000000000000000000000000000000000000000000000000000000000000000"

    # values to build an entry out of:

    chainID ="23985c922e9cdd5ec09c7f52a7c715bc9e26295778ead5d54e30a0a6215783c8" #chain name thisIsAChainName
    entryContent = "hello world"
    externalIDs = ["extid","anotherextid"]

    # Factom constants:
    prefixEC = "592a"
    prefixECsecret = "5db6"


    def send_post_request_with_params_dict(self, method, params_dict):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print r.text
        print params_dict
        print data
        return r.text


    def send_get_request_with_params_dict(self, method, params_dict):
        url = 'http://'+self.factomd_address+'/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "params": params_dict, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text, r.status_code

    def send_get_request_with_method(self, method):
        url = 'http://' + self.factomd_address + '/v2'
        headers = {'content-type': 'text/plain'}
        data = {"jsonrpc": "2.0", "id": 0, "method": method}
        r = requests.get(url, data=json.dumps(data), headers=headers)
        return r.text

    # this function returns the hex encoded Entry Credit public key based on
    # the given privateECKey, which is a hex encoded string
    def ec_addresses_hex(self):
        privatekey = ed25519.SigningKey(self.privateECKey.decode("hex"))
        pubkey = privatekey.get_verifying_key()
        return pubkey.to_ascii(encoding="hex")


    # This function returns the human readable EC address for the private key.
    # It contains a prefix and checksum, to detect typos.
    # https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#human-readable-addresses

    def ec_addresses_human(self):
        addr = self.prefixEC
        addr += self.ec_addresses_hex()
        check = hashlib.sha256(hashlib.sha256(addr.decode("hex")).digest()).digest()
        encoding = base58.b58encode(addr.decode("hex") + check[:4])
        return encoding


    # This function returns the human readable EC private key, based on the hex value from above.
    # It contains a prefix and checksum, to detect typos.
    # https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#human-readable-addresses

    def ec_secret_human(self):
        addr = self.prefixECsecret
        addr += self.privateECKey
        check = hashlib.sha256(hashlib.sha256(addr.decode("hex")).digest()).digest()
        encoding = base58.b58encode(addr.decode("hex") + check[:4])
        return encoding


    # This function connects to a local factomd node and checks the balance for the Entry Credit address

    def get_ec_balance(self):
        # connect to the local factomd instance
        try:
            #url = "http://localhost:8088/v2/entry-credit-balance/" + self.ec_addresses_hex()
            #web_response = requests.get(url)
            #json_return_data = json.loads(web_response.text)
            #return json_return_data["Response"]
            blocks = json.loads(self.send_get_request_with_params_dict('entry-credit-balance', {'address': self.ec_addresses_hex()})[0])
            return blocks['result']['balance']

        except requests.ConnectionError:
            print("Could not connect to the factomd local node.  Is factomd running?")
            return 0


    # This function returns a hex encoded entry based on the values listed at the top
    # https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry

    def construct_entry(self):
        entry = "00"
        entry += self.chainID

        extIdLen = 0
        for e in self.externalIDs:
            extIdLen += len(e)
            extIdLen += 2
        encodeExtIDs = struct.pack('>H', extIdLen)
        entry += encodeExtIDs.encode("hex")

        for e in self.externalIDs:
            extidLen = struct.pack('>H', len(e))
            entry += extidLen.encode("hex")
            entry += e.encode("hex")

        entry += self.entryContent.encode("hex")

        return entry


    # this function returns a hex encoded Entry Hash
    # https://github.com/FactomProject/FactomDocs/blob/master/factomDataStructureDetails.md#entry-hash

    def get_entry_hash(self):
        entryb = self.construct_entry()
        interim = hashlib.sha512(entryb.decode("hex")).digest().encode("hex")
        interim += entryb
        return hashlib.sha256(interim.decode("hex")).digest().encode("hex")


    # this function returns an integer describing the minimum number of entry credits this entry must pay

    def num_entry_credits(self):
        entryLength = len(self.construct_entry())/2 # find the number of bytes the entry takes up
        entryLength -= 35  # the header doesn't count when paying for an entry
        entryLength += 1023 # make the division round up
        entryLength /= 1024 #
        return entryLength


    # then builds the datastructure required to commit an entry, returning in hex format

    def get_entry_commit(self):
        commit = "00"  # version

        millitime = int(time.time() * 1000)  # time() gives floating point, so this tries to be millisecond accurate

        millitimestamp = struct.pack('>Q', millitime)

        # add 6 LS bytes of the millitimestamp to the entry commit
        commit += millitimestamp.encode("hex")[4:]

        commit += self.get_entry_hash()

        ecRequired = struct.pack('b', self.num_entry_credits())
        commit += ecRequired.encode("hex")

        signature = ed25519.SigningKey(self.privateECKey.decode("hex")).sign(commit.decode("hex"), encoding="hex")
        commit += self.ec_addresses_hex()
        commit += signature

        return commit


    # this function checks for a balance on the EC key and returns that balance
    # next it forms an entry and its commit then posts this to the factomd api

    def write_to_factomd(self):
        balance = self.get_ec_balance()

        if 0 < balance:
            print "\nWriting to the Factom API"
            commit = {}
            commit = self.get_entry_commit()
            print "commit = %s" % commit
            blocks = json.loads(self.send_post_request_with_params_dict('commit-entry', {'message': commit}))
            print blocks

            time.sleep(2)
            reveal = {}
            reveal = self.construct_entry()
            print "reveal = %s" % reveal
            #r = requests.post("http://localhost:8088/v1/reveal-entry", data=json.dumps(reveal), headers=headers)
            blocks = json.loads(self.send_post_request_with_params_dict('reveal-entry', {'entry': reveal}))
            print blocks