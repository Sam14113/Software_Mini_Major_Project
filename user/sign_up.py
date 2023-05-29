import pickle
import data_structures
from server import manage_users

def sign_up_org(org_name, first_user):
    return manage_users.add_organisation(org_name, [first_user])

def add_members(org_ID, members):
    for member in members:
        manage_users.add_member(org_ID, member)

