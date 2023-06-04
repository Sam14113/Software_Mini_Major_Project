import pickle

from user import sign_in


def problem_1():
    with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)

    for organisation in organisations:
        print(organisation.name)
        print(organisation.emails, end = '\n\n')

def problem_2():
    with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/database_stub/organisations.pickle', 'rb') as orgs:
        organisations = pickle.load(orgs)

    for org_ID, organisation in enumerate(organisations):
        for member in organisation.members:
            if member.name == 'Britte Siss':
                user_info = sign_in.sign_in_existing_v2(org_ID, member.email)
                print(len(user_info.inbox))

if __name__ == '__main__':
    problem_2()