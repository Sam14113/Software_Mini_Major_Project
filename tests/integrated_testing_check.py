import pickle, json

import data_structures
from user import sign_in

with open("count_calls.txt", "r") as counts:
    count_calls = json.load(counts)

def get_orgs():
    with open("/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/database_stub/organisations.pickle", "rb") as orgs:
        return pickle.load(orgs)

estimations = {}

estimations['organisations'] = count_calls[0]
estimations['users'] = count_calls[0] + count_calls[1]
estimations['groups'] = count_calls[2]
estimations['chats'] = count_calls[2] + count_calls[3]
estimations['messages'] = count_calls[4]

actual = {}

groups = {}

organisations = get_orgs()
actual['organisations'] = len(organisations)
actual['users'] = sum([len(org.members) for org in organisations])
actual['groups'] = 0
actual['chats'] = 0
actual['messages'] = 0

for id, org in enumerate(organisations):
    for member in org.members:
        if sign_in.find_user(member.email) is False:
            member_info = sign_in.sign_in_new_v2(id, member.email)
        try:
            member_info = sign_in.sign_in_existing_v2(id, member.email)
        except AttributeError:
            continue

        for group_ID in member_info.groups:
            group = member_info.groups[group_ID]
            actual['groups'] += (1/len(group.participant_IDs))
            groups[str(group_ID)+'_'+str(id)] = groups.get(str(group_ID)+'_'+str(id), list())
            groups[str(group_ID)+'_'+str(id)].append([member.email, group])

            for chat in group.chats:
                actual['chats'] += (1/len(group.participant_IDs))

                actual['messages'] += (len([i for i in chat.messages if i.type == 'message'])/len(group.participant_IDs))

with open("results.txt", "w") as results:
    print("Expected values:",estimations, file=results)
    print("Actual values:",actual, file=results)
    print(actual == estimations, file=results)
    for group in groups:
        for g in groups[group]:
            if len(g[1].participant_IDs) != len(groups[group]):
                print("HERE'S AN ISSUE!", file = results)

            print({'group_ID':g[1].ID,
                    'perspective':g[0],
                    'group_name': g[1].name,
                    'group_participants':g[1].participant_IDs}, file = results)
        print('\n\n\n', file = results)
    print('_________________________________________________________________\n\n\n', file = results)
    for group in groups: print(data_structures.deobjectify(groups[group]), file = results)




if __name__ == '__main__':
    pass
