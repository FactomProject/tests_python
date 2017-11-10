import os, binascii
from helpers import create_random_string

def generate_random_external_ids_and_content():
    # external ids must be in hex
    name_1 = binascii.b2a_hex(os.urandom(2))
    name_2 = binascii.b2a_hex(os.urandom(2))
    external_ids = [name_1, name_2]

    # content must be in hex
    content = binascii.hexlify(create_random_string(1024))

    return external_ids, content

def commit_failure_data(self, commit_response):
    message = str(commit_response['message'])
    info = str(commit_response['data']['info'])
    entryhash = str(commit_response['data']['entryhash'])
    return message, info, entryhash



