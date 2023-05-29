import pickle

import data_structures
from user import sign_in

from server import communicate, manage_users, validate_user

with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/database_stub/organisations.pickle', 'rb') as orgs:
    organisations = pickle.load(orgs)

success = 0
fail = []
test1_private = sign_in.sign_in_existing_v2(0, 'test1@clarity.com')
test2_private = sign_in.sign_in_existing_v2(0, 'test2@clarity.com')
test3_private = sign_in.sign_in_existing_v2(0, 'test3@clarity.com')
test4_private = sign_in.sign_in_existing_v2(0, 'test4@clarity.com')
breakpoint()
test1_sk = test1_private.rsa_sk
test2_sk = test2_private.rsa_sk
test3_sk = test3_private.rsa_sk
test4_sk = test4_private.rsa_sk

test1_aes = test1_private.aes
test2_aes = test2_private.aes
test3_aes = test3_private.aes
test4_aes = test4_private.aes

test1_groups = test1_private.groups

first = str(data_structures.deobjectify(test1_groups)).split("'messages':")
second = "\n".join(first[1:])
third = second.split("'dtype': \"<class 'data_structures.Message'>\"}")
for i, val in enumerate(third):
    if "'type': 'message'" not in val:
        print(i, val)

for member in organisations[0].members:
    inbox = member.get_inbox()
    if member.email == 'test2@clarity.com':
        for i, message in enumerate(inbox):
            try:
                test2_private.decrypt_message(message)
                success += 1
            except:
                fail.append([2, i])
    if member.email == 'test3@clarity.com':
        for i, message in enumerate(inbox):
            try:
                test3_private.decrypt_message(message)
                success += 1
            except:
                fail.append([3, i])

    if member.email == 'test4@clarity.com':
        for i, message in enumerate(inbox):
            try:
                test4_private.decrypt_message(message)
                success += 1
            except:
                fail.append([3, i])

print(success)
print(fail)

