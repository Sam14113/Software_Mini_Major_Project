from data_structures import *
import pickle
from time import sleep

if __name__ == "__main__":

    members = []
    for i in range(10):
        members.append(Member(f'Name {i}',f'randomemail{i}@gmail.com'))
    manage_users.add_organisation('Random', members)
    for member in members:
        sign_in.sign_in_new(0, member.email, b'randompassword')


if __name__ == "__main__":
    with open('/server/database_stub/organisations.pickle', 'rb') as organisations:
        orgs = pickle.load(organisations)
        print(deobjectify(orgs))
