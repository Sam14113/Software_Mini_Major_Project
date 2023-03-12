import data_structures
import pickle

def complete_user(org_ID, email, salt, pwd_hash, rsa_pk, rsa_sk_bundle):
    with open('database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    for member_ID, member in enumerate(organisations[org_ID].members):
        if member.email == email:
            member.update(
                salt=salt, pwd_hash=pwd_hash,
                rsa_pk=rsa_pk, rsa_sk_bundle=rsa_sk_bundle)
            organisations[org_ID].members[member_ID] = member
            with open('database_stub/organisations.pickle', 'wb') as orgs:
                pickle.dump(organisations, orgs)
            return data_structures.Member_Private(member)
