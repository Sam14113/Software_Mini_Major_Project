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