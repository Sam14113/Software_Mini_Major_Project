from server import communicate

def send_message(org_ID, recipient_IDs, sender_rsa_sk, message):
    rsa_pks = communicate.get_rsa_pks(org_ID, recipient_IDs)
    encrypted_messages = []
    for recipient_ID in recipient_IDs:
        try: encrypted_messages.append(message.encrypt(rsa_pks[recipient_ID], sender_rsa_sk))
        except KeyError: raise KeyError(
            "It seems like one or more participants haven't finished signing up, so we can't include them yet.")

    communicate.send_message(org_ID, recipient_IDs, encrypted_messages)