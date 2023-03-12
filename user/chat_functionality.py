import argparse
import os

import slixmpp
from slixmpp.test import SlixTest
from cryptography.hazmat.primitives import serialization
from nacl import public
from slixmpp import plugins
from Crypto.Cipher import AES
import json
import asyncio
import rsa
from auxiliary import *


class XMPP_rsa_pk_storage(slixmpp.ClientXMPP):
    'A bot to distribute rsa public keys to other users as needed'

    def __init__(self, jid, pwd_hash, server_rsa_sk):
        super().__init__(self, jid, pwd_hash)
        self.rsa_pks = {}
        self.server_rsa_sk = server_rsa_sk
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.interpret_message)

    def start(self, event):
        self.get_roster()
        self.send_presence()

    def interpret_message(self, message):
        if message['subject'] == 'GET':
            self.send_rsa_pk(message['from'])

        if message['subject'] == 'SET':
            body = message['body']
            body = json.loads((rsa.decrypt(body, self.server_rsa_sk)).decode())

            aes, nonce, tag = body['AES info']
            main = body['main']
            aes_cipher = AES.new(aes, AES.MODE_EAX, nonce)
            main = aes_cipher.decrypt_and_verify(main, tag).decode()
            self.update_rsa_pk(message['from'], main)

    def update_rsa_pk(self, jid, rsa_pk):
        self.rsa_pks[jid] = rsa_pk

    def send_rsa_pk(self, mto):
        self.send_message(mto=mto, msubject='RSA QUERY RESPONSE', mbody=rsa_pk)  # NEED TO SIGN


class XMPP_user(slixmpp.ClientXMPP):
    'A class for each user, facilitating chat functionality'

    def __init__(self, name, jid, pwd_hash, rsa_pk, rsa_sk, server_jid, server_rsa_pk, chats):
        super().__init__(self, jid, pwd_hash)
        self.name = name
        self.chats = chats
        self.rsa_pk = rsa_pk
        self.rsa_sk = rsa_sk
        self.server_rsa_pk = server_rsa_pk
        self.server_jid = server_jid
        self.rsa_pks = {}
        self.messages = []

        self.register_plugin('xep_0045')  # Multi User Chat specification
        self.muc = self.plugin['xep_0045']
        self.register_plugin('xep_0313')  # Message Archive Management specification
        self.mam = self.plugin['xep_0313']

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.received_message)
        self.add_event_handler('muc::invite', self.accept_invite)

    async def start(self, event):
        self.get_roster()
        self.send_presence()
        self.messages = await self.mam.retrieve()['mam']['results']

        # self.messages = self.enter_chats()
        # self.join_room()

    def received_message(self, message):
        self.messages.append(message)

    def enter_chats(self):
        messages = []
        for chat_jid, chat in self.chats:
            self.plugin['xep_0045'].join_muc_wait(chat, self.name)
            messages.append([chat_jid, self.get_items(chat_jid, 500)])

        return messages

    def accept_invite(self, invitation):
        chat = invitation['mucroom']
        self.plugin['xep_0045'].join_muc_wait(chat)

    def get_items(self, chat_jid, max_messages):
        messages_request = self.plugin['xep_0045'].get_mucconfig(chat_jid)
        messages_request['muc#history_length'] = max_messages
        history = self.plugin['xep_0045'].get_room_config(chat_jid, messages_request)
        messages = history['muc']['history']
        return messages

    def send_group_item(self, chat_jid, mtype, message, **kwargs):
        """Sends an item to each member of a chat individually, and indicates what chat its from.
        This is important: End-To-End encryption doesn't work well for group chat messages,
        so every message in this program is sent as a DM.
        MUC Rooms are only used to support roles and affiliations."""
        recipients = (
                self.muc.get_affiliation_list(chat_jid, 'member') +
                self.muc.get_affiliation_list(chat_jid, 'admin') +
                self.muc.get_affiliation_list(chat_jid, 'owner')
        )
        mbody = {'chat_jid': chat_jid, 'message': message}
        mbody.update(kwargs)
        mbody = json.dumps(mbody).encode()

        aes, mbody_encrypted, nonce, tag = encrypt_with_random_AES(mbody)
        aes_info = json.dumps({'aes': aes, 'nonce': nonce, 'tag': tag}).encode()
        for recipient in recipients:
            # SEND MESSAGE TO MEMBER_JID
            recipient_rsa_pk = self.rsa_pks[recipient]
            aes_info_encrypted = rsa.encrypt(aes_info, recipient_rsa_pk)
            mbody_packaged = json.dumps({'aes': aes_info_encrypted, 'main': mbody_encrypted})
            self.send_message(mto=recipient, mtype=mtype, mbody=mbody_encrypted)

    def add_member(self, chat_jid, member_jid):
        self.muc.set_affiliation(chat_jid, 'member', jid=member_jid)

    def remove_member(self, chat_jid, member_jid):
        self.muc.set_affiliation(chat_jid, 'none', jid=member_jid)

    def make_admin(self, chat_jid, member_jid):
        self.muc.set_affiliation(chat_jid, 'admin', jid=member_jid)

    def create_chat(self, chat_jid, member_jids):
        self.muc.join_muc_wait(chat_jid, self.name)
        for jid in member_jids:
            self.add_member(chat_jid, jid)

    ''' parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='Server JID', required=True)
    parser.add_argument('-p', '--password', help='Password', required=True)
    parser.add_argument('-j', '--jid', help='JID', required=True)
    args = parser.parse_args()

    server_jid = args.server
    password = args.password
    name = args.jid'''


class TestMyXMPP(SlixTest):
    def setUp(self):
        self.mock_server = self.get_mock_xmpp("localhost")
        self.

    def test_connect(self):
        server_jid = 'server@localhost'

        server_rsa_pk, server_rsa_sk = rsa.newkeys(1024)
        alice_rsa_pk, alice_rsa_sk = rsa.newkeys(1024)
        bob_rsa_pk, bob_rsa_sk = rsa.newkeys(1024)
        charlie_rsa_pk, charlie_rsa_sk = rsa.newkeys(1024)

        chats = []
        Alice = XMPP_user('Alice', 'Alice@localhost', 'password', alice_rsa_pk, alice_rsa_sk, server_jid,
                          server_rsa_pk, chats)
        Alice.connect()
        Alice.process()
        Bob = XMPP_user('Bob', 'Bob@localhost', 'password', bob_rsa_pk, bob_rsa_sk, server_jid, server_rsa_pk,
                        chats)
        Bob.connect()
        Bob.process()
        Alice.create_chat('ChatAB', ['Bob@localhost'])
        Alice.send_group_item('ChatAB', 'chat', 'Hey!')
        print(Alice.messages)
        print("_____________________________")
        print(Bob.messages)
        print("_____________________________")
        print("_____________________________")
        Bob.create_chat('ChatABC', ['Alice@localhost', 'Charlie@localhost'])
        Alice.send_group_item('ChatABC', 'chat', 'Hey!')
        print(Alice.messages)
        print("_____________________________")
        print(Bob.messages)
        print("_____________________________")
        print("_____________________________")
        Charlie = XMPP_user('Charlie', 'Charlie@localhost', 'password', charlie_rsa_pk, charlie_rsa_sk, server_jid,
                            server_rsa_pk, chats)
        Charlie.connect()
        Charlie.process()
        print(Charlie.messages)
        print("_____________________________")
        print("_____________________________")
        Charlie.send_group_item('ChatABC', 'chat', 'Made it!')
        print(Alice.messages)
        print("_____________________________")
        print(Bob.messages)
        print("_____________________________")
        print(Charlie.messages)
        print("_____________________________")
