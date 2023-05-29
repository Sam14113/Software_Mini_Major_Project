import time
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

import user.sign_in, user.send, user.chat_functionality_v2
import auxiliary
from server import communicate
from user.sign_up import add_members
from server.validate_user import upload_verification_hash, verify_user, check_is_verified
from server.communicate import get_inbox
from string import ascii_uppercase, digits
from Crypto.Random import random
from Crypto.Hash import SHA256
import rsa
import data_structures as ds

current_group = None
current_chat = None
info = []

class ClearableScreen(Screen): # NOTE: This class definition was written by ChatGPT
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        self.clear_inputs(self)

    def clear_inputs(self, widget):

        if isinstance(widget, TextInput):
            widget.text = ''

        elif isinstance(widget, CheckBox):
            widget.active = False

        for child in widget.children:
            self.clear_inputs(child)


class BlankScreen(ClearableScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):

        for component in self.components:
            component.parent.remove_widget(component)
            self.ids['main_box_layout'].add_widget(component)
            self.ids['main_box_layout'].children[-1].opacity = 1


class GetVerifiedScreen(BlankScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        super().on_pre_enter()
        verification_code = ""
        for i in range(8):
            verification_code += random.choice(ascii_uppercase + digits)
        hash_object = SHA256.new()
        hash_object.update(verification_code.encode())
        verification_hash = hash_object.hexdigest()
        upload_verification_hash(self.manager.info['name'].text, self.manager.info['user_info']['name'], verification_hash)
        self.ids['code'].text = verification_code

    def check(self):
        if check_is_verified(self.manager.info['org_ID'], self.manager.info['user_info']['name'])[0]:
            self.manager.info['user_info_2'] = user.sign_in.sign_in_new_v2(self.manager.info['org_ID'], self.manager.info['email'])
            self.manager.current = 'RegisterOrgMembersScreen'

class VerifyMemberScreen(BlankScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def verify(self, verifiee_email, code):
        #rsa_sk = self.manager.info['user info'].rsa_sk
        #verification_hash_encrypted = rsa.encrypt(code.encode(), rsa_sk)
        verify_user(int(self.manager.info['org_ID']), str(self.manager.info['user_info']['name']), verifiee_email, code)

class LoginAuth0Screen(BlankScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        #self.manager.info['login_URL'] = next(self.manager.info['login_generator'])
        self.ids['code'].text = next(self.manager.info['login_generator'])

    def redirect(self, user_info):
        self.manager.info['email'] = user_info['name']
        user_exists = user.sign_in.find_user(user_info['name'])
        if not user_exists and not self.manager.info['existing_org']:
            self.manager.current = 'RegisterOrgWelcomeScreen'
        elif not user_exists and self.manager.info['existing_org']:

            self.manager.current = 'GetVerifiedWelcomeScreen'
        else:
            self.manager.info['org_ID'] = user_exists[1]
            if user_exists[2]: # If the user has already signed up themselves
                self.manager.info['user_info_2'] = user.sign_in.sign_in_existing_v2(user_exists[1], self.manager.info['user_info']['name'])
            else:
                self.manager.info['user_info_2'] = user.sign_in.sign_in_new_v2(user_exists[1], self.manager.info['user_info']['name'])

            self.manager.current = 'HomeScreen'


class ScreenManagement(ScreenManager):
    pass
    #info = {'login_generator':None}


class OrgDataEntry(GridLayout):
    def __init__(self, **kwargs):
        super(OrgDataEntry, self).__init__(**kwargs)
        self.cols = 1
        self.spacing = 30
        self.row_count = 0
        self.row_info = []
        for _ in range(8): self.add_row()

    def add_row(self):
        row = BoxLayout(orientation='horizontal', spacing = 30)
        row.add_widget(Label(text="    "+str(self.row_count+1),
                             color = (0, 0, 0, 1),
                             size_hint_x = 1))
        name = TextInput(size_hint_x = 50, hint_text='Full Name',multiline=False)
        row.add_widget(name)
        email = TextInput(size_hint_x = 50, hint_text='Email', multiline=False)
        row.add_widget(email)
        self.row_info.append([name, email])
        self.add_widget(row)
        self.row_count += 1

    def make_members(self, org_id):
        members = []

        for row in self.row_info:
            name = row[0].text
            email = row[1].text
            if name:
                members.append(ds.Member(name, email))

        add_members(org_id, members)

    def get_emails(self):
        return [row[1].text for row in self.row_info if row[1].text]

class CreateGroupScreen(BlankScreen):

    def create_group(self):
        user_ID = self.manager.info['user_info_2'].email
        org_ID = self.manager.info['org_ID']
        sender_rsa_sk = self.manager.info['user_info_2'].rsa_sk
        group_name = self.ids['group_name'].text
        participant_IDs = self.ids['participants'].get_emails() + [user_ID]

        group = user.chat_functionality_v2.create_group(user_ID, org_ID, group_name, participant_IDs, sender_rsa_sk)

        #Updating group list
        self.manager.info['user_info_2'].groups[group.ID] = group

        #Navigating to home screen
        self.manager.current = 'HomeScreen'
        #global info
        #info = self.manager.info['user_info_2']

class CreateChatScreen(BlankScreen):

    def create_chat(self):
        global current_group
        global current_chat
        user_ID = self.manager.info['user_info_2'].email
        org_ID = self.manager.info['org_ID']
        group_ID = current_group.ID
        sender_rsa_sk = self.manager.info['user_info_2'].rsa_sk

        chat_name = self.ids['chat_name'].text

        chat = user.chat_functionality_v2.create_chat(user_ID, org_ID, current_group, chat_name, sender_rsa_sk)

        #Updating group list
        self.manager.info['user_info_2'].groups[group_ID].add_chats([chat])

        #Navigating to home screen
        self.manager.current = 'HomeScreen'

class SidebarList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 1
        self.spacing = 0
        self.buffer = 0

        self.groups = BoxLayout(orientation = 'vertical')
        self.add_widget(self.groups)
        self.chats = BoxLayout(orientation = 'vertical')
        self.add_widget(self.chats)


    def update_group_list(self, groups):
        self.groups.clear_widgets()
        print(type(groups))
        for group_ID in groups:
            group = groups[group_ID]
            button = SidebarButton(text = group.name, ds_object = group, classification = 'group')

            self.groups.add_widget(button)

        print(len(self.groups.children))

    def update_chat_list(self):
        global current_group
        chats = current_group.chats
        self.chats.clear_widgets()
        for i, chat in enumerate(chats):
            chat_button = SidebarButton(text = chat.name, ds_object = chat, classification = 'chat')
            self.chats.add_widget(chat_button)

    def change_current_group(self, group, instance):
        global current_group
        current_group = group

    def change_current_chat(self, chat, instance):
        global current_chat
        current_chat = chat

    def clear_buttons(self):
        self.groups.clear_widgets()
        self.chats.clear_widgets()

    def refresh(self, groups):
        global current_group
        #inbox = get_inbox(org_ID, info.email)
        #info.update_inbox(inbox)
        #info.process_inbox()
        self.clear_buttons()
        self.update_group_list(groups)
        if current_group: self.update_chat_list()

class SidebarButton(Button):
    ds_object = ObjectProperty()
    classification = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self):
        global current_group
        global current_chat

        if self.classification == 'group':
            current_group = self.ds_object
        elif self.classification == 'chat':
            current_chat = self.ds_object


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        self.refresh(None)
        Clock.schedule_interval(self.refresh, 2)

    def refresh(self, instance):
        global current_chat
        print("REFRESHING")
        self.ids['message_list'].refresh()

        self.manager.info['user_info_2'].inbox = communicate.get_inbox(
            self.manager.info['org_ID'], self.manager.info['user_info_2'].email)

        self.manager.info['user_info_2'].process_inbox()
        communicate.clear_inbox(self.manager.info['org_ID'], self.manager.info['user_info_2'].email)
        print(self.manager.info['user_info_2'].groups)
        #print("USER_INFO_2:", ds.deobjectify(self.manager.info['user_info_2']))
        groups = self.manager.info['user_info_2'].groups
        self.ids['sidebar_list'].refresh(groups)

        #self.ids['groups_label'].text = "\n".join([groups[group_ID].name for group_ID in groups])
        self.ids['sidebar_list'].update_group_list(groups)

    def send_message(self, text):
        global current_group
        global current_chat

        user_ID = self.manager.info['user_info_2'].email
        message_ID = auxiliary.get_new_random_ID([])
        org_ID = self.manager.info['user_info_2'].org_ID
        group_ID = current_group.ID
        chat_ID = current_chat.ID
        recipient_IDs = [ID for ID in current_group.participant_IDs if ID != user_ID]

        user_info_2 = self.manager.info['user_info_2']
        message = ds.Message(message_ID, group_ID, chat_ID, time.time(), user_info_2.email, None, {'text': text},'message')

        self.manager.info['user_info_2'].groups[group_ID].get_chat(chat_ID).messages.append(message)
        print("MESSAGE APPENDED")

        user.send.send_message(org_ID, recipient_IDs, user_info_2.rsa_sk, message)
        print("MESSAGE SENT")

class MessageList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 10
        self.buffer = 5
        #self.messages = BoxLayout(orientation = 'vertical')
        #self.messages.add_widget(Label(color = (0, 0, 0, 0.5), text = 'Not a real message'))
        #self.add_widget(self.messages)


    def refresh(self, reset = True):
        global current_chat
        if reset: self.clear_widgets()
        print("UPDATING MESSAGES")

        if not current_chat: return
        messages = current_chat.messages
        print("MESSSAGES:", len(messages))

        for message in messages:
            if message.type == 'message':
                self.add_widget(Label(color = (0, 0, 0, 0.5), text = message.sender_ID))
                self.add_widget(Label(color = (0, 0, 0, 1), text = message.content['text']))
                self.add_widget(Label())

        print(len(self.children))
        #print(len(self.messages.children))




kv = Builder.load_file("gui_specs_v2.kv")
class ClarityApp(App):
    def build(self):
        return kv

if __name__ == '__main__':
    ClarityApp().run()