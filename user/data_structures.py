class Member():
    #For each user, a member object will be created for them

    def __init__(self, name, email, privilege_status):
        self.name = name
        self.email = email
        self.salt = None
        self.pwd_hash = ""
        self.rsa_pk = ""
        self.rsa_sk_bundle = {
            'encrypted sk':("", ""),
            'tag':"",
            'nonce': ""
        }
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