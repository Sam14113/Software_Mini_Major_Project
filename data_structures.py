from auxiliary import *

class Message():

    def __init__(self, ID, timestamp, sender_ID, content):
        self.ID = ID
        self.timestamp = timestamp
        self.sender_ID = sender_ID
        self.content = content

class Chat():

    def __init__(self, ID, group_ID):
        self.ID = ID
        self.group_ID = group_ID
        self.message_IDs = []
        self.unread_count = 0

    def new_message(self, message_ID):
        self.message_IDs.append(message_ID)
        self.unread_count += 1

    def read_chat(self):
        self.unread_count = 0


class Group():

    def __init__(self, ID):
        self.ID = ID
        self.chat_IDs = []
        self.participant_IDs = []

    def add_participants(self, participant_IDs):
        for ID in participant_IDs:
            self.participant_IDs.append(ID)
        bubble_sort(self.participant_IDs) #may remove later on, if I don't want it sorted

    def add_chats(self, chat_IDs):
        for chat_ID in chat_IDs:
            self.chat_IDs.append(chat_ID)
        bubble_sort(self.chat_IDs)

    def remove_participant(self, participant_ID):
        index = binary_search(self.participant_IDs, participant_ID, strict = True)
        self.participant_IDs.pop(index)


class Member():
    #For each user, a member object will be created for them

    def __init__(self, ID, name, email, privilege_status):
        self.ID = ID
        self.name = name
        self.email = email
        self.privilege_status = privilege_status

    def update(self, **kwargs):
        #Go through each item and assign
        #Due to difference in string vs var name, we can't use a loop
        if 'name' in kwargs.keys():
            self.name = kwargs['name']

        if 'email' in kwargs.keys():
            self.email = kwargs['email']

        if 'salt' in kwargs.keys():
            self.salt = kwargs['salt']

        if 'pwd_hash' in kwargs.keys():
            self.pwd_hash = kwargs['pwd_hash']

        if 'rsa_pk' in kwargs.keys():
            self.rsa_pk = kwargs['rsa_pk']

        if 'rsa_sk_bundle' in kwargs.keys():
            self.rsa_sk_bundle = kwargs['rsa_sk_bundle']

        if 'privilege_status' in kwargs.keys():
            self.privilege_status = kwargs['privilege_status']


class Member_Private():
    #Upon login, object created from member_database object in order to

    def __init__(self, member):
        self.name = member.name
        self.email = member.email
        self.rsa_sk_bundle = member.rsa_sk_bundle

    def add_keys(self, aes, rsa_sk):
        self.aes = aes
        self.rsa_sk = rsa_sk


class Organisation():
    #For each organisation, an organisation object will be created for it

    def __init__(self, name, members):
        self.name = name
        self.members = members
        self.emails = [member.email for member in members]
            #emails are stored separately so that they can be accessed more easily

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        self.members.remove(member)

def deobjectify(obj, path = tuple()):
    path = list(path)
    receipt = []
    if type(obj) in (list, tuple, set):
        if type(obj) == tuple: obj = list(obj)

        for i, val in enumerate(obj):
            if type(val) not in (int, str, float):
                obj[i], mini_receipt = deobjectify(val, path + [i])
                for j in mini_receipt:
                    if j[0] not in (int, str, float, list, tuple, set, dict):
                        receipt = receipt + mini_receipt
                        break

        return [obj, receipt]


    else:
        if type(obj) != dict: dictionary = obj.__dict__
        else: dictionary = obj
        for key in dictionary:
            dictionary[key], mini_receipt = deobjectify(dictionary[key], key)
            for j in mini_receipt:

        return [dictionary, receipt]

if __name__ == '__main__':
    members = []
    for i in range(10):
        members.append(Member((i+3)**3, f'Name {i}',f'randomemail{i}@gmail.com', 0))
    org = Organisation('Microsoft', members)
    print(org.members)
    print(org.name)
    print(deobjectify(org))