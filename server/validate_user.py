from database_stub.organisations import organisations

def validate_user(org_ID, email, hash_candidate):
    for member in organisations[org_ID].members:
        if member.email == email:
            if member.pwd_hash == hash_candidate and member.pwd_hash:
                return (member.rsa_sk_encrypted, member.)
            else:
                return False
    else: raise ValueError
