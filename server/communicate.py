import pickle
from auxiliary import *


def get_rsa_pks(org_ID, member_IDs):
    """ Finds and returns the RSA public keys of the given members as a dictionary, keyed by member ID

    :param int org_ID: The relevant Organisation ID
    :param list[str] member_IDs: The member IDs of the queried members
    :return dict: RSA public keys of queried members, keyed by member ID
    """

    rsa_pks = {}  # The dictionary of RSA public keys (initially empty)
    with open("../database_stub/organisations.pickle", "rb") as orgs:  # The pickled list of organisations
        organisation = pickle.load(orgs)[org_ID]
    for member in organisation.members:
        if member.ID in member_IDs:
            rsa_pks[member.ID] = member.rsa_pk  # Update the dictionary with the relevant public key
            member_IDs.remove(member.ID)
    if len(member_IDs) > 0:
        error_message = "We couldn't find any members with the following emails: "
        for member_ID in member_IDs:
            error_message += '; ' + member_ID
        raise KeyError(error_message)

    return rsa_pks

def claim_available_group_ID(org_ID):
    """ Finds and returns an available group ID in the given organisation. Then marks as used

    :param int org_ID: The relevant Organisation ID
    :return int: An available group ID in the organisation
    """

    with open("../database_stub/organisations.pickle", "rb") as orgs:  # The pickled list of organisations
        organisations = pickle.load(orgs)

    group_ID = get_new_random_ID(organisations[org_ID].group_IDs)
    organisations[org_ID].add_group(group_ID)



    with open("../database_stub/organisations.pickle", "wb") as orgs:  # The pickled list of organisations
        pickle.dump(organisations, orgs)

    return group_ID

def send_message(org_ID, recipient_IDs, encrypted_messages):
    """ Sends encrypted messages to the inboxes of the given recipients.

    Flow: Typically called by user.send_message, after encryption

    :param int org_ID: The relevant Organisation ID
    :param list[str] recipient_IDs: The member IDs of the recipients
    :param encrypted_messages: The encrypted messages for each recipient in the same order as their IDs
    :type encrypted_messages: list[data_structures.Message]
    :return: None
    """

    with open("../database_stub/organisations.pickle", "rb") as orgs:  # The pickled list of organisations
        organisations = pickle.load(orgs)
        organisation = organisations[org_ID]

    for recipient_index, recipient_ID in enumerate(recipient_IDs):
        try:
            #print(list(map(lambda member:member.ID, organisation.members)))
            #print(recipient_ID)

            # Perform a mixed search to find the member in the list of members
            member_index = mixed_search(
                organisation.members, recipient_ID, organisation.len_sorted, key = lambda member: member.ID)

            # Put the message in their inbox
            organisation.members[member_index].add_message(encrypted_messages[recipient_index])

        except ValueError: # Occurs if search fails, i.e recipient_ID not in member_IDs or member_IDs not sorted
            raise ValueError("Recipient ID not found in list of members")

    organisations[org_ID] = organisation

    with open("../database_stub/organisations.pickle", "wb") as orgs:
        pickle.dump(organisations, orgs)


def get_inbox(org_ID, member_ID):
    """Returns the inbox of the given member

    :param int org_ID: The Organisation ID of the queried member
    :param str member_ID: The member ID of the queried member
    :return list[data_structures.Message]: The inbox of the queried member
    """

    with open("../database_stub/organisations.pickle", "rb") as orgs:
        organisations = pickle.load(orgs)

    organisation = organisations[org_ID]
    member = organisation.get_member(member_ID)
    inbox = member.get_inbox()

    organisations[org_ID] = organisation

    with open("../database_stub/organisations.pickle", "wb") as orgs:
        pickle.dump(organisations, orgs)

    return inbox

def clear_inbox(org_ID, member_ID):
    """Clears the inbox of the given member
    :param int org_ID: The Organisation ID of the queried member
    :param str member_ID: The member ID of the queried member
    :return: None
    """

    with open("../database_stub/organisations.pickle", "rb") as orgs:
        organisations = pickle.load(orgs)
        organisation = organisations[org_ID]
        for member in organisation.members:
            if member.ID == member_ID:
                member.clear_inbox()

    with open("../database_stub/organisations.pickle", "wb") as orgs:
        pickle.dump(organisations, orgs)

if __name__ == '__main__':
    with open("../database_stub/organisations.pickle", "rb") as orgs:
        organisations = pickle.load(orgs)
        for organisation in organisations:
            for member in organisation.members:
                member.clear_inbox()

