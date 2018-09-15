class Room(object):

    #El nombre del cuarto
    name = None
    #El ID del dueño del cuarto
    owner = None
    type = None
    #Solo se guardara el id de los clientes
    invited_clients = None
    accepted_clients = None

    msg_list = None

    def __init__(self, name, owner, invited = [], type = 'general'):
        self.name = name
        self.owner = owner
        self.invited_clients = invited
        self.type = type
        self.accepted_clients = []
        self.msg_list = []

    def guests(self):
        return self.accepted_clients

    def client_is_accepted(self, client_name):
        return (client_name in accepted_clients)

    def add_msg(self, msg):
        self.msg_list.append(msg)

    def add_invitation(self, client):
        if (self.type != 'personal' or self.name == 'global'):
            self.invited_clients.append(client)

    def accept_guest(self, client):
        if (client in self.invited_clients):
            index = self.invited_clients.index(client)
            del self.invited_clients[index]
            self.accepted_clients.append(client)
