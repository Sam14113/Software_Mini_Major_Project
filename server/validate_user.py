import pickle
import rsa
from Crypto.Hash import SHA256
from time import time

import auxiliary
import data_structures as DS


def validate_email(email):
    """ Checks if an email is in the database.

    :param str email:
    :return: One of the following:
        - False if the email is not in the database. Otherwise,
            - [False, org_ID, has_rsa_pk] if the user is waiting to be verified.
            - [True, org_ID, has_rsa_pk] otherwise.
            In both cases, org_ID is the organisation ID of the user
    """

    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)

    for org_ID, org in enumerate(organisations):
        try:
            user = auxiliary.linear_search_value(org.members, email, lambda member:member.email)
            break
        except ValueError:
            continue
    else: return False

    has_rsa_pk = 'rsa_pk' in dir(user)

    return [True, org_ID, has_rsa_pk]


def validate_pwd(org_ID, user_email, hash_candidate):
    """ Checks if password hash matches database value.

    NOTE: This function is based on the OLD password flow BEFORE AUTH0.
    It is DANGEROUS as it allows for a Pass the Hash attack
    The dangers were not too significant as the AES key was not recoverable
    However, it has been replaced by the AUTH0 flow.

    The function has been preserved to be modified if we recreate the password flow.

    :param org_ID: The organisation ID of the user
    :param user_email: The email of the user
    :param hash_candidate: The hash of the password which the user inputted
    :return:
        - [False] if the hashes don't match (i.e password is incorrect)
        - [True, Ds.Member_Private] if the hashes match
    """

    raise Exception("The 'validate_pwd' function is not safe to use")

    # Checks if password hash matches database value
    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    for member in organisations[org_ID].members:
        if member.email == user_email:
            if member.pwd_hash == hash_candidate:
                return [True, DS.Member_Private(member)]
            else:
                return [False]
    else:
        raise ValueError

def get_member_private(org_ID, user_ID):
    """ Gets the private member object for the user

    :param int org_ID: The organisation ID which the user belongs to
    :param str user_ID: The ID of the queried user
    :return: private_member object
    """
    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)

    try:
        # Find member in the organisation
        prefix_len = organisations[org_ID].len_sorted
        member = auxiliary.mixed_search_value(
            organisations[org_ID].members, user_ID, prefix_len, key = lambda member: member.ID)
    except ValueError:
        raise ValueError("Member not found in organisation")

    private_member = DS.Member_Private(member)
    private_member.update_inbox(member.get_inbox())
    return private_member


def upload_verification_hash(name, email, hash):
    """

    :param str email: The email of the user to be verified
    :param bin hash: The SHA256 hash of the verification code for that user
    :return:
    """

    with open('../database_stub/verification_hashes.pickle', 'rb') as hashes:
        hashes_list = pickle.load(hashes)

    timestamp = time()
    try:
        index = auxiliary.linear_search(hashes_list, email, lambda list_item: list_item[0])
        hashes_list[index] = [name, email, hash, timestamp]

    except ValueError:
        hashes_list.append([name, email, hash, timestamp])

    print(hashes_list)

    with open('../database_stub/verification_hashes.pickle', 'wb') as hashes:
        pickle.dump(hashes_list, hashes)

def get_verification_hashes(org_ID):
    #TODO Delete this function

    raise Exception("This function will be deleted in the end as it is not used anymore")
    with open('../database_stub/verification_hashes.pickle', 'rb') as hashes:
        return pickle.load(hashes)

def verify_user(org_ID, verifier_ID, verifiee_email, code):
    """ Allows an existing member of an organisation to verify a user with their verification code.

    :param int org_ID: org_ID which the user belongs to
    :param str verifier_ID: the ID of the member who is verifying the user
    :param str verifiee_email: the email of the user to be verified
    :param str email: user email
    :param str code: the verification code as plaintext
    :return: None
    """

    with open('../database_stub/verification_hashes.pickle', 'rb') as hashes:
        hashes_list = pickle.load(hashes)

    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
        organisation = organisations[org_ID]

    # Find the hash of the code, for comparison
    hash_object = SHA256.new()
    hash_object.update(code.encode())
    hash = hash_object.hexdigest()

    for name_candidate, email_candidate, hash_candidate, timestamp in hashes_list:
        if email_candidate == verifiee_email and hash_candidate == hash:
            if time() - timestamp >= 3600000000000:
                raise TimeoutError("Verification code has expired")
            break
    else:
        raise ValueError("Either the email or the verification code is incorrect")

    try:
        member_index = auxiliary.linear_search(organisation.members, verifiee_email, lambda member: member.email)
    except ValueError:
        member = DS.Member(name_candidate, verifiee_email)
        member.update(verification = verifier_ID)

        organisation.add_member(member)

        organisations[org_ID] = organisation

        with open('../database_stub/organisations.pickle', 'wb') as orgs:
            pickle.dump(organisations, orgs)
            return

    raise ValueError("Member already verified")



def check_is_verified(org_ID, email):
    #TODO Stringdoc
    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    for ID, org in enumerate(organisations):
        if ID == org_ID:
            for member in org.members:
                if member.email == email:
                    if 'verification' in dir(member):
                        return [True, member.verification]
                    else:
                        return [False]
            else:
                return [False]
    else:
        raise ValueError

if __name__ == '__main__':
    #print(validate_email('test1@test.com'))
    """new_code = 'ABCDEFGH'

    hash_object = SHA256.new()
    hash_object.update(new_code.encode())
    new_hash = hash_object.hexdigest()

    upload_verification_hash('test3@clarity.com', new_hash)

    print("NEW HASH:", new_hash)
    with open('../database_stub/verification_hashes.pickle', 'rb') as hashes:
        hashes_list = pickle.load(hashes)
        for email, hash in hashes_list:
            print(email, hash)"""

    #verify_user(0, 'test1@clarity.com', 'ABCDEFGH')
    print(check_is_verified(0, 'test3@clarity.com'))