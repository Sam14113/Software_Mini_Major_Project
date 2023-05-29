import auxiliary
import time
import user
import data_structures as ds
import pickle

def create_group(user_ID, org_ID, group_name, participant_IDs, sender_rsa_sk):
    # Creating group

    group_ID = auxiliary.get_new_random_ID([])
    group = ds.Group(group_ID)
    group.rename(group_name)
    group.add_participants(participant_IDs)

    # Creating group invitation

    invitation_message_ID = auxiliary.get_new_random_ID([])
    invitation = ds.Message(
        invitation_message_ID, group_ID, 0, time.time(), user_ID, None, {'group_name': group_name},
        'group_invitation')

    # Creating alert to add participants, so that all users know who else is there

    participants_alert_message_ID = auxiliary.get_new_random_ID([])
    participants_alert = ds.Message(
        participants_alert_message_ID, group_ID, 0, time.time(), user_ID, None, {'participant_IDs': participant_IDs},
        'add_participants')

    # Sending both alerts to all recipients
    participant_IDs.remove(user_ID) # So that the user doesn't receive the alerts
    user.send.send_message(org_ID, participant_IDs, sender_rsa_sk, invitation)
    user.send.send_message(org_ID, participant_IDs, sender_rsa_sk, participants_alert)

    return group
def create_chat(user_ID, org_ID, group, chat_name, sender_rsa_sk):
    # Creating chat

    chat_ID = auxiliary.get_new_random_ID([])
    chat = ds.Chat(chat_ID, group.ID)
    chat.rename(chat_name)

    # Creating chat alert

    alert_ID = auxiliary.get_new_random_ID([])
    alert = ds.Message(alert_ID, group.ID, 0, time.time(), user_ID, None, {'chats': [chat]}, 'add_chats')

    # Sending alert to all group members
    recipient_IDs = [ID for ID in group.participant_IDs if ID != user_ID]
    user.send.send_message(org_ID, recipient_IDs, sender_rsa_sk, alert)


    return chat
