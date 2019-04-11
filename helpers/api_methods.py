import os, binascii
from .helpers import create_random_string

def generate_random_external_ids_and_content():
    # external ids must be in hex
    name_1 = binascii.b2a_hex(os.urandom(2)).decode('UTF-8')
    name_2 = binascii.b2a_hex(os.urandom(2)).decode('UTF-8')
    external_ids = [name_1, name_2]

    # content must be in hex
    content = binascii.hexlify(create_random_string(1024).encode('UTF-8')).decode('UTF-8')

    return external_ids, content


