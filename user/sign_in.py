from hashlib import scrypt as hash
from Crypto.Cipher import AES
import rsa as RSA
def find_user(email):
    pass

def sign_in_existing(org_ID, email, pwd_input, salt):
    AES_key = hash(pwd_input, salt = salt, n=16384, r=8, p=1)
    pwd_hash = hash(pwd_input, salt = salt, n=16384, r=8, p=1)
    #Here, the pwd_hash should be com