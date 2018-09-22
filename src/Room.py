"""
A room can have multiple clients, invitations a name, an owner, a message list and even a type of room.
To generate HTML documentation for this module use the command:

    pydoc -w src.Room

"""

class Room(object):
    """
    Room encapsulates all the funtionalities a room can have.
    It encapsulates:
        name - The name of the room
        owner - The id of the owner
        type - The type of room
        invited_clients - A list of the id of the invited clients
        accepted_clients - A list of the id of the clients that have joined the room
        msg_list - The message list
    """

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
        """
        Create a room.

        :param name: The name of the room
        :param owner: The room's owner
        :param invited: A list of invited clients
        :param type: The type of room
        """

        self.name = name
        self.owner = owner
        self.invited_clients = invited
        self.type = type
        self.accepted_clients = []
        self.msg_list = []

    def guests(self):
        """
        Returns the id of the clients that have joined the room.

        :return: the id of the clients that have joined the room.
        """

        return self.accepted_clients

    def client_is_accepted(self, client_name):
        """
        Tells whether or not the client with that name is in the accepted clients

        :return: True if it is in, false otherwise
        """

        return (client_name in accepted_clients)

    def add_msg(self, msg):
        """
        Adds a message to the room's message list

        :param msg: The message
        """

        self.msg_list.append(msg)

    def add_invitation(self, client):
        """
        Adds an invitation for a client

        :param client: The client to add
        """

        if (self.type != 'personal' or self.name == 'global'):
            self.invited_clients.append(client)

    def accept_guest(self, client):
        """
        Accepts a client if and only if the client was invited first.

        :param client: The client that joined the room.
        """

        if (client in self.invited_clients):
            index = self.invited_clients.index(client)
            del self.invited_clients[index]
            self.accepted_clients.append(client)
