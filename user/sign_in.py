import pickle

import Crypto.Random
import rsa, json
from hashlib import scrypt as hash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from server import validate_user, manage_users

def find_user(email):
    return validate_user.validate_email(email)

def sign_in_new(org_ID, email, pwd_input):
    #hash password
    salt = get_random_bytes(16)
    hash1 = hash(pwd_input, salt = salt, n=16384, r=8, p=1)
    aes = hash1[:16]
    pwd_hash = hash(hash1, salt = salt, n = 16384, r=8, p=1)

    #create RSA key
    rsa_pk, rsa_sk = rsa.newkeys(2048)
    rsa_sk_file = rsa_sk.save_pkcs1()
    #encrypt rsa_sk
    aes_cipher = AES.new(aes, AES.MODE_EAX)
    nonce = aes_cipher.nonce
    rsa_sk_encrypted, tag = aes_cipher.encrypt_and_digest(rsa_sk_file)
    rsa_sk_bundle = {
        "encrypted sk": rsa_sk_encrypted,
        "tag": tag,
        "nonce": nonce
    }

    #update information in database
    user_info = manage_users.complete_user(org_ID, email, salt, pwd_hash, rsa_pk, rsa_sk_bundle)
    user_info.add_keys(aes, rsa_sk)

    return user_info




def sign_in_existing(org_ID, email, pwd_input, salt):
    #hash password
    hash1 = hash(pwd_input, salt = salt, n=16384, r=8, p=1)
    aes = hash1[:16]
    pwd_hash = hash(hash1, salt = salt, n=16384, r=8, p=1)

    #validate user & get info
    user_info = validate_user.validate_pwd(org_ID, email, pwd_hash)
    if not user_info[0]: raise Exception("Invalid password")
    user_info = user_info[1]

    #get RSA secret key
    aes_cipher = AES.new(aes, AES.MODE_EAX, user_info.rsa_sk_bundle["nonce"])
    rsa_sk_file = aes_cipher.decrypt_and_verify(user_info.rsa_sk_bundle["encrypted sk"], user_info.rsa_sk_bundle["tag"])
    rsa_sk = rsa.PrivateKey.load_pkcs1(rsa_sk_file)


    #store keys in user_info object
    user_info.add_keys(aes, rsa_sk)

    return user_info

def sign_in_new_v2(org_ID, email):
    #randomly generate AES key
    aes_key = get_random_bytes(16)

    #store AES key locally
    with open(f"/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/user/user_data/{email}_aes.bin", 'xb') as aes_file:
        aes_file.write(aes_key)

        # create RSA key
        rsa_pk, rsa_sk = rsa.newkeys(2048)
        rsa_sk_file = rsa_sk.save_pkcs1()
        # encrypt rsa_sk
        aes_cipher = AES.new(aes_key, AES.MODE_EAX)
        nonce = aes_cipher.nonce
        rsa_sk_encrypted, tag = aes_cipher.encrypt_and_digest(rsa_sk_file)
        rsa_sk_bundle = {
            "encrypted sk": rsa_sk_encrypted,
            "tag": tag,
            "nonce": nonce
        }
        test_cipher = AES.new(aes_key, AES.MODE_EAX, nonce = nonce)
        rsa_sk_decrypted = test_cipher.decrypt(rsa_sk_encrypted)

        # update information in database and get relevant info back
        user_info = manage_users.complete_user(org_ID, email, rsa_pk, rsa_sk_bundle)
        user_info.add_keys(aes_key, rsa_sk)

        return user_info


def sign_in_existing_v2(org_ID, email):
    user_info = validate_user.get_member_private(org_ID, email)

    #get AES key
    with open(f"/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/user/user_data/{email}_aes.bin", 'rb') as aes_file:
        aes_key = aes_file.read()

    #get RSA secret key
    aes_cipher = AES.new(aes_key, mode = AES.MODE_EAX, nonce = user_info.rsa_sk_bundle["nonce"])
    rsa_sk_file = aes_cipher.decrypt_and_verify(user_info.rsa_sk_bundle["encrypted sk"], user_info.rsa_sk_bundle["tag"])
    rsa_sk = rsa.PrivateKey.load_pkcs1(rsa_sk_file)

    # store keys in user_info object
    user_info.add_keys(aes_key, rsa_sk)

    try:
        with open(f"/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/user/user_data/{email}_groups.bin", 'rb') as groups_file:
            groups_info = pickle.load(groups_file)
            aes_cipher = AES.new(aes_key, AES.MODE_EAX, groups_info["nonce"])
            groups = aes_cipher.decrypt_and_verify(groups_info['groups'], groups_info['tag'])
            groups = pickle.loads(groups)
            user_info.groups = groups
    except FileNotFoundError:
        pass

    user_info.process_inbox()

    return user_info
