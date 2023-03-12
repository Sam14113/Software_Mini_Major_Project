import json
from data_structures import deobjectify

# Globals

def forward_package(package, recipient_ID):
    return b'FWD' + recipient_ID.to_bytes(4, 'big') + package


def validate_email(email):
    # store email as variable 1
    email = email.encode()
    instructions = b'LET' + int(1).to_bytes(1, 'big') + b'STR' + len(email).to_bytes(1, 'big') + email

    # validate that email
    instructions += b'VLD' + b'EML' + int(1).to_bytes(1, 'big')

    return instructions

def add_organisation(organisation):

# ORG >> MBR
def add_member(org_ID, member):
    # Store member user as variable 1
    name = member.name.encode()
    email = member.email.encode()
    status = int(0).to_bytes(1,'big')  # STUB until status becomes a thing

    member_info = (int(4).to_bytes(1, 'big') + member.ID.to_bytes(4, 'big') +
                   len(name).to_bytes(1, 'big') + name +
                   len(email).to_bytes(1, 'big') + email +
                   int(1).to_bytes(1, 'big') + status)
    member_info = deobjectify(member)
    member_info = json.dumps(member_info)
    instructions = b'LET' + int(1).to_bytes(1, 'big') + b'MBR' + len(member_info).to_bytes(1,'big') + member_info

    instructions += b'IN2' + b'ORG' + org_ID.to_bytes(4, 'big') + b'IN1' + b'MBR' + b'ADD' + int(1).to_bytes(1, 'big')

    return instructions

def validate_email(email):
    email = email.encode()
    instructions = b'LET' + int(1).to_bytes(1, 'big') + b'STR' + len(email).to_bytes(1, 'big') + email

    instructions += b'IN1' + b'ORG' + b'VAL' + b'EML' + int(1).to_bytes(1, 'big')

    return instructions
# ORG >> MBR >> DTA
def validate_password(org_ID, member_ID, hash_candidate):
    # store hash candidate as variable 1
    instructions = b'LET' + int(1).to_bytes(1, 'big') + b'STR' + len(hash_candidate).to_bytes(1,
                                                                                              'big') + hash_candidate

    # validate password
    instructions += (b'IN2' + b'ORG' + org_ID.to_bytes(4, 'big') + b'MBR' + member_ID.to_bytes(4, 'big') +
                     b'IN1' + b'DTA' + b'VLD' + b'PWD' + int(1).to_bytes(1, 'big'))

    return instructions

def remove_member(org_ID, member_ID):
    pass