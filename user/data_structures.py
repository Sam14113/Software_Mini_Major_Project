class Member():
    #For each user, a member object will be created for them

    def __init__(self, name, email, privilege_status):
        self.name = name
        self.email = email
        self.salt = ""
        self.pwd_hash = ""
        self.rsa_pk = ""
        self.rsa_sk_encrypted = ""
        self.privilege_status = privilege_status


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