import inspect
import sys
from pydoc import locate

import auxiliary
import rsa
import pickle
import math
from Crypto.Cipher import AES
from auxiliary import *
from server import manage_users, communicate
from user import sign_in


class Message():
    """
    Message class. This is not just for traditional messages, but for any communication between users
    """

    def __init__(self, ID, group_ID, chat_ID, timestamp, sender_ID, signature, content, type):
        """ Constructs Message object

        :param int ID: message ID
        :param int group_ID: group ID which the message belongs to
        :param int chat_ID: chat ID which the message belongs to
        :param float timestamp: The time when the message was sent
        :param int sender_ID: sender ID of the message
        :param None signature: Not used anymore - exists for backwards compatibility
        TODO If time permits, remove signature from everywhere
        :param dict content: The content of the message - this changes with the message type
        :param type: Message type. See process_inbox for message types
        """

        self.ID = ID
        self.type = type
        self.group_ID = group_ID
        self.chat_ID = chat_ID
        self.signature = signature
        self.timestamp = timestamp
        self.sender_ID = sender_ID
        self.content = content
        self.replies = []

    def encrypt(self, recipient_rsa_pk, sender_rsa_sk):
        """ Encrypts the message so that only the recipient can decrypt it

        It also signs the message with the private key of the sender for verification purposes.

        :param recipient_rsa_pk: The RSA public key of the recipient
        :param sender_rsa_sk: The RSA private key of the sender
        :return: Dictionary with all relevant information to decrypt message
        """

        pkl = pickle.dumps(self)
        aes, encrypted_message, nonce, tag = auxiliary.encrypt_with_random_AES(pkl) # Encrypts the message with AES
        aes_encrypted = rsa.encrypt(aes, recipient_rsa_pk) # Encrypts the AES key with the rsa pk of the recipient
        signature = rsa.sign(aes_encrypted, sender_rsa_sk, 'SHA-256') # Signs the AES key with the rsa sk of the sender
        message_bundle = {'encrypted_message': encrypted_message,
                          'aes_encrypted': aes_encrypted,
                          'nonce': nonce,
                          'tag': tag,
                          'signature': signature}
        return message_bundle

    def add_reply(self, reply):
        """Adds reply to a message. Must be done before encryption"""
        self.replies.append(reply)


class Chat():
    """
    Chat class, which stores messages
    """
    def __init__(self, ID, group_ID):
        """ Constructs Chat object

        :param ID: Chat ID
        :param group_ID: Group ID which the chat belongs to
        """
        self.ID = ID
        self.name = 'Chat'
        self.group_ID = group_ID
        self.messages = []
        self.alerts = []
        self.unread_count = 0

    def add_message(self, message):
        self.messages.append(message)
        self.unread_count += 1

    def add_reply(self, message_ID, reply):
        for message in self.messages:
            if message_ID == message.ID:
                message.add_reply(reply)

    def add_alert(self, alert):
        #TODO Is this used?
        self.alerts.append(alert)
        self.unread_count += 1

    def read_chat(self):
        self.unread_count = 0

    def rename(self, name):
        self.name = name


class Group():

    def __init__(self, ID):
        self.ID = ID
        self.name = 'Group'
        main_chat = Chat(0, ID)
        main_chat.rename('Main')
        self.chats = [main_chat]
        self.participant_IDs = []

    def rename(self, name):
        self.name = name

    def add_participants(self, participant_IDs):
        for ID in participant_IDs:
            self.participant_IDs.append(ID)
        self.participant_IDs = bubble_sort(self.participant_IDs)  # may remove later on, if I don't want it sorted

    def add_chats(self, chats):
        for chat in chats:
            self.chats.append(chat)

    def get_chat(self, chat_ID):
        for chat in self.chats:
            if chat.ID == chat_ID:
                return chat

    def update_chat(self, chat_updated):
        for i, chat in enumerate(self.chats):
            if chat.ID == chat_updated.ID:
                self.chats[i] = chat

    def remove_participant(self, participant_ID):
        index = linear_search(self.participant_IDs, participant_ID)
        self.participant_IDs.pop(index)

    def delete_chat(self, chat_ID):
        index = linear_search_value(self.chats, chat_ID, key = lambda chat: chat.ID)
        self.participant_IDs.pop(index)


class Member():
    # For each user, a member object will be created for them

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.ID = email
        self.privilege_status = 'member'
        self.org_ID = None
        self.inbox = []

    def update(self, **kwargs):
        # Go through each item and assign
        # Due to difference in string vs var name, we can't use a loop

        update_dict = kwargs.keys()
        if 'name' in update_dict:
            self.name = kwargs['name']

        if 'org_ID' in update_dict:
            self.org_ID = kwargs['org_ID']

        if 'ID' in update_dict:
            self.ID = kwargs['ID']

        if 'email' in update_dict:
            self.email = kwargs['email']

        if 'salt' in update_dict:
            self.salt = kwargs['salt']

        if 'pwd_hash' in update_dict:
            self.pwd_hash = kwargs['pwd_hash']

        if 'rsa_pk' in update_dict:
            self.rsa_pk = kwargs['rsa_pk']

        if 'rsa_sk_bundle' in update_dict:
            self.rsa_sk_bundle = kwargs['rsa_sk_bundle']

        if 'privilege_status' in update_dict:
            self.privilege_status = kwargs['privilege_status']

        if 'verification' in update_dict:
            self.verification = kwargs['verification']

    def add_message(self, message):
        self.inbox.append(message)
        with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/user/log.txt', 'a') as f:
            print("A message was sent to", self.ID, file = f)
            print(self.ID, "has", len(self.inbox), 'messages', file = f)

    def get_inbox(self):
        inbox = self.inbox
        self.inbox = []
        return inbox

    def clear_inbox(self):
        self.inbox = []


class Member_Private():
    # Upon login, object created from member_database object
    # Gives users the information they need to operate

    def __init__(self, member):
        self.name = member.name
        self.email = member.email
        self.ID = member.ID

        try: self.rsa_sk_bundle = member.rsa_sk_bundle
        except AttributeError:
            print(deobjectify(member))
            raise

        if member.org_ID or member.org_ID == 0: self.org_ID = member.org_ID
        else: self.org_ID = sign_in.find_user(member.email)[1]
        self.inbox = []
        self.groups = dict()

    def add_keys(self, aes, rsa_sk):
        self.aes = aes
        self.rsa_sk = rsa_sk

    def update_inbox(self, inbox):
        self.inbox = inbox

    def decrypt_message(self, bundle):

        # Get all information
        encrypted_message = bundle['encrypted_message']
        aes_encrypted = bundle['aes_encrypted']
        nonce = bundle['nonce']
        tag = bundle['tag']
        signature = bundle['signature']

        # Decrypt the aes key
        aes = rsa.decrypt(aes_encrypted, self.rsa_sk)

        # Decrypt the message
        aes_cipher = AES.new(aes, AES.MODE_EAX, nonce)
        try:
            message = pickle.loads(aes_cipher.decrypt_and_verify(encrypted_message, tag))
        except:
            raise ValueError('Message was corrupted')

        # Verify the signature
        sender_rsa_pk = communicate.get_rsa_pks(self.org_ID, [message.sender_ID])[message.sender_ID]
        try:
            rsa.verify(aes_encrypted, signature, sender_rsa_pk)
        except:
            raise ValueError('Invalid signature')

        return message

    def process_inbox(self):
        for message in self.inbox:
            try:
                message = self.decrypt_message(message)
            except ValueError:
                raise ValueError('Invalid message')

            # Update messages with the new message, and take action if neccesary

            group = self.groups.get(message.group_ID)
            if group is None and message.type == 'group_invitation':

                """with open('/Users/adam.gottlieb/PycharmProjects/Software_Mini_Major_Project/user/log.txt', 'a') as f:
                    print(self.ID, "acknowledged group invitation from", message.sender_ID, file = f)"""

                group = Group(message.group_ID)
                group.rename(message.content['group_name'])
                # breakpoint()
            elif group is None:
                raise ValueError('Group not found')

            chat = group.get_chat(message.chat_ID)

            if message.type == 'message':
                chat.add_message(message)

            elif message.type == 'reply':
                chat.add_reply(message.content['parent_ID'], message)

            else:
                chat.add_message(message)

                if message.type == 'set_group_name':
                    group.rename(message.content['group_name'])

                elif message.type == 'set_chat_name':
                    group.rename(message.content['chat_name'])

                elif message.type == 'add_participants':
                    group.add_participants(message.content['participant_IDs'])

                elif message.type == 'remove_participant':
                    group.remove_participant(message.content['participant_ID'])

                elif message.type == 'add_chats':
                    group.add_chats(message.content['chats'])

                elif message.type == 'remove_chat':
                    group.remove_chat(message.content['chat_ID'])

            # Update with the updated version of the chat
            group.update_chat(chat)
            self.groups.update({group.ID: group})

        # Encrypt updated groups using AES

        aes_cipher = AES.new(self.aes, AES.MODE_EAX)
        nonce = aes_cipher.nonce
        groups_encrypted, tag = aes_cipher.encrypt_and_digest(pickle.dumps(self.groups))
        groups_encrypted_info = pickle.dumps({'nonce': nonce, 'tag': tag, 'groups': groups_encrypted})

        # Store encrypted updated groups on device

        with open(
                f'/user/user_data/{self.email}_groups.bin',
                'wb') as groups_file:
            groups_file.write(groups_encrypted_info)

        # Clear local inbox
        self.inbox = list()


        # DEBUGGING

        """debug = str(deobjectify(self.groups))
        indent = 0
        latest = 0
        for i, char in enumerate(debug):
            if char == '{':
                print('   ' * indent + debug[latest:i])
                latest = i
                indent += 1

            if char == '}':
                print('   ' * indent + debug[latest:i])
                indent += -1
                print('   ' * indent + debug[i])
                latest = i + 1"""


class Organisation():
    # For each organisation, an organisation object will be created for it

    def __init__(self, name=None, members=tuple()):
        self.name = name
        self.members = auxiliary.bubble_sort(list(members), lambda member:member.ID)
        self.len_sorted = len(self.members)
        self.emails = [member.email for member in members]
        self.group_IDs = []
        # emails are stored separately so that they can be accessed more easily
        #self.open_verification_hashes = []

    def get_org_ID(self):
        return sign_in.find_user(self.members[0].email)[1]

    def add_member(self, member):
        member.org_ID = self.get_org_ID()

        self.members.append(member)
        self.emails.append(member.email)
        if len(self.members) - self.len_sorted > 4*math.log2(len(self.members)):
            self.members = auxiliary.bubble_sort(
                self.members,
                key = lambda member:member.ID,
                max_passes = len(self.members)-self.len_sorted)

            self.len_sorted = len(self.members)


    def remove_member(self, member_ID):
        index = auxiliary.mixed_search(self.members, member_ID, self.len_sorted, lambda member:member.ID)
        if index < self.len_sorted: self.len_sorted += -1
        self.members.pop(index)

    def get_member(self, member_ID):
        member = auxiliary.mixed_search_value(self.members, member_ID, self.len_sorted, lambda member:member.ID)
        return member

    def update_member(self, member_ID, member):
        index = auxiliary.mixed_search(self.members, member_ID, self.len_sorted, lambda member:member.ID)
        self.members[index] = member

    def add_group(self, group_ID):
        if group_ID not in self.group_IDs:
            self.group_IDs.append(group_ID)
        else: raise ValueError('Group ID already used')


def deobjectify(obj):
    if type(obj) in (list, tuple, set):
        result = list(obj)

        for i, val in enumerate(result):
            if type(val) not in (int, str, float, bytes, type(None)):
                result[i] = deobjectify(val)
        # print(obj)
        return result


    elif type(obj) in (int, str, float, bytes, type(None)):
        return obj
    elif type(obj) == bytes:
        return {'dtype': str(type(bytes)), 'value': obj.decode()}
    else:
        if type(obj) == rsa.PrivateKey:
            return {'dtype': rsa.PrivateKey, 'value': obj.save_pkcs1()}
        elif type(obj) == rsa.PublicKey:
            return {'dtype': rsa.PublicKey, 'value': obj.save_pkcs1()}
        elif type(obj) != dict:
            dictionary = obj.__dict__
            dictionary['dtype'] = str(type(obj))
        else:
            dictionary = obj
        for key in dictionary:
            dictionary[key] = deobjectify(dictionary[key])
        return dictionary


def objectify(skeleton):
    if type(skeleton) in (list, tuple, set):
        if type(skeleton) == tuple: skeleton = list(skeleton)

        for i, val in enumerate(skeleton):
            if type(val) not in (int, str, float):
                skeleton[i] = objectify(val)
        return skeleton

    elif type(skeleton) in (int, str, float):
        return skeleton

    elif type(skeleton) == dict:
        skeleton_type = skeleton['type']
        for type_candidate in (Message, Chat, Group, Member, Member_Private, Organisation):
            if str(type_candidate) == skeleton_type:
                skeleton_type = type_candidate
                break

        else:
            if skeleton_type in (str(rsa.PrivateKey), str(rsa.PublicKey)):
                skeleton_type.load_pkcs1(skeleton['value'])
            if skeleton_type == str(bytes):
                return skeleton['value'].encode()
        # if skeleton_type not in (Message, Chat, Group, Member, Member_Private, Organisation):
        # raise ValueError(f'Type {skeleton_type} not supported')
        obj = skeleton_type()
        for key in skeleton:
            if key == 'type':
                continue
            obj.__dict__[key] = objectify(skeleton[key])
        return obj


if __name__ == '__main__':
    """members = []
    for i in range(10):
        members.append(Member(f'Name {i}',f'randomemail{i}@gmail.com'))
    manage_users.add_organisation('Random', members)
    for member in members:
        print(sign_in.sign_in_new(0, f'randomemail{i}@gmail.com', b'randompassword'))"""
