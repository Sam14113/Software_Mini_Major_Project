import rsa
if __name__ == '__main__':
    pk, sk = rsa.newkeys(2048)
    pk_file = pk.save_pkcs1()
    sk_file = sk.save_pkcs1()
    with open('database_stub/server_pk.bin', 'wb') as file:
        file.write(pk_file)
    with open('server/server_sk.bin', 'wb') as file:
        file.write(sk_file)