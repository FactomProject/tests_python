import random
import string

def create_random_string(char_nr):
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_nr))