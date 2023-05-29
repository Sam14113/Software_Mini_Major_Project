import rsa

import data_structures
import pickle

def complete_user(org_ID, email, rsa_pk, rsa_sk_bundle):
    """Completes user upon either being verified or opening an organisation.

    Called from sign_in_existing
    Their status is changed from 'invitee' to 'member'
    Their RSA public key and an encrypted version of their RSA private key are stored in the database.

    :param int org_ID: The ID of the user's organisation
    :param str email: The email of the user
    :param rsa.PublicKey rsa_pk: The RSA public key of the user
    :param dict rsa_sk_bundle: The RSA secret key of the user encrypted with their AES with nonce, tag
    :return: data_structures.Member_Private: A member private object for the user (see there)
    """

    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    for member_ID, member in enumerate(organisations[org_ID].members):
        if member.email == email:
            member.update(privilege_status = 'member', rsa_pk=rsa_pk, rsa_sk_bundle=rsa_sk_bundle)
            organisations[org_ID].members[member_ID] = member
            with open('../database_stub/organisations.pickle', 'wb') as orgs:
                pickle.dump(organisations , orgs)
            return data_structures.Member_Private(member)


def add_organisation(name, members):
    """ Creates new organisation and adds it to the database.

    :param str name: The name of the organisation
    :param list members: A list of the initial members of the organisation as member objects
    """

    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    organisations.append(data_structures.Organisation(name, members))
    with open('../database_stub/organisations.pickle', 'wb') as orgs:
        pickle.dump(organisations, orgs)
    return len(organisations)-1

def add_member(org_ID, member):
    """Adds a member to the organisation

    :param int org_ID: The organisation ID of the relevant organisation
    :param member: The Member object to add to the organisation
    :return: None
    """

    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    organisations[org_ID].add_member(member)
    with open('../database_stub/organisations.pickle', 'wb') as orgs:
        pickle.dump(organisations , orgs)

def clear_orgs():
    """ Clears the database of organisations.

    :return: None
    """

    with open('../database_stub/organisations.pickle', 'wb') as orgs:
        pickle.dump([], orgs)

def clear_hashes():
    """ Clears the database of verification hashes.

    :return: None
    """
    with open('../database_stub/verification_hashes.pickle', 'wb') as hashes:
        pickle.dump([], hashes)

if __name__ == '__main__':
    from user import sign_in
    """clear_orgs()"""
    #clear_hashes()
    """with open('../database_stub/organisations.pickle',
              'rb') as orgs:
        orgs = pickle.load(orgs)
    print(len(orgs))"""
    with open('../database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)
    """for i, organisation in enumerate(organisations):
        for j, member in enumerate(organisation.members):
            member.update(org_ID = i)
            #user_info = sign_in.sign_in_existing_v2(i, member.email)
            for message in member.inbox:
                print(data_structures.deobjectify(pickle.loads(rsa.decrypt(message, user_info.rsa_sk))))"""

    """with open('../database_stub/organisations.pickle', 'wb') as orgs:
        pickle.dump(organisations, orgs)"""

    first = str(data_structures.deobjectify(organisations)).split('}, {')
    print("\n".join(first))
