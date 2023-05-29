import rsa, time
from Crypto.Cipher import AES
from Crypto.Random import random, get_random_bytes
from auxiliary import *


# Package Format:
# Sender ID, timestamp, AES key, tag, nonce encrypted in RSA (256 ->> 4, 4, 16, 16, 16)
# RSA Signature of previous using SHA-256 (256 ->> 32)
# Instructions Encrypted in AES


def wrap_package(instruction, sender_ID, recipient_pk, sender_sk, inbox):

    #Encrypts instruction with AES (Random Key)
    aes = get_random_bytes(16)
    aes_cipher = AES.new(aes, AES.MODE_EAX)
    nonce = aes_cipher.nonce
    instruction, tag = aes_cipher.encrypt_and_digest(instruction)

    header = sender_ID.to_bytes(4,'big') + time.time().to_bytes(4, 'big') + aes + tag + nonce  # Creates pkg header with sender_ID and AES info.
    header_encrypted = rsa.encrypt(header, recipient_pk)  # Encrypts header with RSA

    signature = rsa.sign(header, sender_sk, 'SHA-256')  # Signs header to prove identity

    # TEMPORARY SOLUTION: Stores Package in inbox folder
    name = 'pkg' + str(random.randrange(10**8)) + '.bin'

    # name = 'pkg100.bin'
    with open(inbox+name, 'ab') as server_package_file:
        server_package_file.write(header_encrypted)
        server_package_file.write(signature)
        server_package_file.write(instruction)


if __name__ == '__main__':
    instruction = ('A very long instruction'*500).encode()
    recipient_ID = 3023573928
    sender_ID = 5126543
    sender_pk, sender_sk = rsa.newkeys(2048)
    inbox = '/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/server/inbox/'

    with open('/server/database_stub/server_pk.bin', 'rb') as server_rsa_pk_file:
        server_rsa_pk = server_rsa_pk_file.read()
        server_pk = rsa.PublicKey.load_pkcs1(server_rsa_pk)

    wrap_package(instruction, sender_ID, server_pk, sender_sk, inbox)
    with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/server/server_sk.bin', 'rb') as server_sk_file:
        server_rsa_sk = server_sk_file.read()
        server_rsa_sk = rsa.PrivateKey.load_pkcs1(server_rsa_sk)

    with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/server/inbox/pkg100.bin', 'rb') as file:
        contents = file.read()

        header = rsa.decrypt(contents[:256],server_rsa_sk)

        signature = contents[256:512]
        rsa.verify(header, signature, sender_rsa_pk)

        sender_ID = int.from_bytes(header[:4], 'big')
        timestamp = header[4:8]
        aes = header[8:24]
        tag = header[24:40]
        nonce = header[40:]

        encrypted_package = contents[512:]
        aes_cipher = AES.new(aes, AES.MODE_EAX, nonce)
        unencrypted_package = aes_cipher.decrypt_and_verify(encrypted_package, tag)

        print(unencrypted_package)
