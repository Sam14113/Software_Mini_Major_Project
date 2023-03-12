import pickle
import data_structures as DS


def validate_email(email):
    with open('database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    for id, org in enumerate(organisations):
        if email in org.emails:
            user = [i for i in org.members if i.email == email]
            user = user[0]
            if user.salt:
                return [True, id, user.salt]
            else:
                return [False, id]
    else: return False

def validate_pwd(org_ID, user_ID, hash_candidate):
    #Checks if password hash matches database value
    with open('database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    for member in organisations[org_ID].members:
        if member.ID == user_ID:
            if member.pwd_hash == hash_candidate:
                return [True, DS.Member_Private(member)]
            else:
                return [False]
    else:
        raise ValueError
