import pickle

import data_structures

if __name__ == '__main__':
    with open("/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/database_stub/organisations.pickle", 'rb') as orgs:
        organisations = pickle.load(orgs)
        for organisation in organisations:
            for member in organisation.members:
                member.clear_inbox()

    with open("/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/database_stub/organisations.pickle", 'wb') as orgs:
        pickle.dump(organisations, orgs)

    print(data_structures.deobjectify(organisations))

