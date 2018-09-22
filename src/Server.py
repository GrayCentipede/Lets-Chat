from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from socket import error as SocketError
from threading import Thread
import signal

from .Event import Event
from .Room import Room

"""
A class for the Server.
To generate HTML documentation for this module use the command:

    pydoc -w src.Server

"""

class Server(object):
    """
    Server will be able to handle multiple connections, messages, rooms and invitations.
    It encapsulates:
        buffer_size - The size of the buffer
        host - The host where the server is allocated
        port - The port where the server is allocated
        server - The server's socket
        id_autoincrement - An id that will autoincrement every time a connection is accepted
        lobbies - A list of all the lobbies(rooms) in the server
        clients - A list of all the connections that are available
        server_id - The server's connection name
        is_on - Tells whether or not the server is on
    """

    buffer_size = 1024
    host = None
    port = None
    server = None
    id_autoincrement = 0
    lobbies = None
    clients = None
    server_id = '__SERVER__'
    is_on = 0

    class Connection(object):
        """
        Connection will hold all the neccesary information of a connection that has been accepted in the
        server.
        It encapsulates:
            id - The conection id
            name - The connection's name
            address - The connection's address
            socket - The connection's socket
            invitations - The invitations a connection can have
            has_identified - Tells whether or not a connection has identified to the server
        """

        id = 0
        name = None
        address = None
        socket = None
        invitations = None
        has_identified = False

        def __init__(self, id, name, address, socket):
            """
            Constructs a connection.

            :param id: The connection's id
            :param name: The connection's name
            :param address: The connection's addressee
            :param socket: The connection's socket
            """

            self.id = id
            self.name = name
            self.address = address
            self.socket = socket
            self.invitations = []

    def create_new_conection(self, name, address, socket):
        """
        Creates a new connection, increments the id_autoincrement and returns the new connection

        :param name: The name of the connection
        :param address: The address of the connection
        :param socket: The socket of the connection
        """

        connection = self.Connection(self.id_autoincrement, name, address, socket)
        self.id_autoincrement += 1
        return connection

    def __init__(self, port, host = '0.0.0.0', num_conections = 10, mode = 'normal'):
        """
        Constructs a server.
        A server with normal mode behaves like a normal server.
        A server with debug mode prints the users and rooms that it has.
        A server with unittest mode is only used for testing, it will not print a thing

        :param port: The server's port
        :param host: The server's host
        :param num_conections: The server's number conections that it can handle
        :param type: The server's type.
        """

        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.lobbies = []
        self.clients = []
        self.mode = mode
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_conection = self.create_new_conection(self.server_id, self.address, self.server)
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

        try:
            self.server.bind(self.address)
            self.server.listen(num_conections)
            self.lobbies.append(Room('PUBLIC', 0, [], type = 'personal'))
            self.is_on = 1
            if (self.mode != 'unittest'):
                print('Server {} is now awaiting for connections at port {}'.format(host, port))

        except Exception as e:
            if (self.mode != 'unittest'):
                print('An error has occurred while trying to lift the server: ' + str(e))

    def close(self):
        """
        Closes the server.
        """

        if (self.mode != 'unittest'):
            print('Shutting down server {}'.format(self.host))
        self.send_msg_to_all(self.server_conection, 'The server {} is shutting down. Thanks for staying.'.format(self.host))
        self.server_status = 0
        copy = self.clients.copy()
        for client in copy:
            self.disconnect_client(client)

        self.server.close()

    def get_client_by_name(self, name):
        """
        Returns the connection that has the given name.

        :param name: The client's name
        :return: None if it does not exists, the found connection otherwise
        """

        for conn in self.clients:
            if (conn.name == name):
                return conn

        return None

    def invalid_event(self, client):
        """
        In case the connection send an invalid command it will be returned a message of invalid event.

        :param client: the client.
        """

        msg = []
        msg.append('...INVALID MESSAGE\n')
        msg.append('...VALID MESSAGES ARE:\n')
        msg.append('...IDENTIFY username\n')
        msg.append('...STATUS userStatus = {ACTIVE, AWAY, BUSY}\n')
        msg.append('...MESSAGE username messageContent\n')
        msg.append('...PUBLICMESSAGE messageContent\n')
        msg.append('...CREATEROOM roomname\n')
        msg.append('...INVITE roomname user1 user2...\n')
        msg.append('...JOINROOM roomname\n')
        msg.append('...ROOMESSAGE roomname messageContent\n')
        msg.append('...DISCONNECT\n')
        client.socket.send(bytes(''.join(msg), 'utf8'))

    def must_identify(self, client):
        """
        Tells the client that it must identify first.

        :param client: The client.
        """

        msg ='...MUST IDENTIFY FIRST\n...TO IDENTIFY: IDENTIFY USERNAMER\n'
        client.socket.send(bytes(msg, 'utf8'))

    def identify_client(self, client, name):
        """
        Identifies or updates a client's name, it fails if the name is already in use.

        :param client: The client.
        :param name: The client's name
        """

        conn = self.get_client_by_name(name)
        already_in_use = True if conn != None else False

        if (already_in_use or name == self.server_id):
            client.socket.send(bytes('...USERNAME NOT AVAILABLE\n', 'utf8'))

        else:
            for lobby in self.lobbies:
                if (lobby.type == 'personal' and lobby.name == client.name):
                    lobby.name = name

            for conn in self.clients:
                if (client.id == conn.id):
                    conn.name = name
                    break

            client.has_identified = True
            client.socket.send(bytes('...SUCCESFUL IDENTIFICATION\n', 'utf8'))


    def users(self, client):
        """
        Returns a list of users to the client.

        :param client: The client
        """

        user_list = ' '.join([conn.name for conn in self.clients])
        client.socket.send(bytes(user_list + '\n', 'utf8'))

    def get_personal_room(self, author_id, addressee_name):
        """
        Returns a personal room where only the author and the addressee are in.

        :param author_id: The author's id
        :param addressee_name: The addressee's name

        :return: None if it does not exists, the found room otherwise
        """

        addressee = self.get_client_by_name(addressee_name)
        for lobby in self.lobbies:
            if (lobby.type == 'personal'):
                a = (lobby.owner == author_id and addressee.id in lobby.accepted_clients)
                b = (lobby.owner == addressee.id and author_id in lobby.accepted_clients)
                if (a or b):
                    return lobby

        return None

    def get_room(self, owner_id, name):
        """
        Returns the room whose owner's id is the given one in the arguments and it's name is the same
        as the one given in the arguments.

        :param owner_id: The owner's id
        :param name: The room's name
        :return: None if it does not exists, the found room otherwise
        """

        for lobby in self.lobbies:
            if (lobby.owner == owner_id and lobby.name == name):
                return lobby

        return None

    def send_status(self, client, status):
        """
        Sends the client's status to everyone connected to the server.

        :param client: The client
        :param status: The new client's status
        :return: None if and only if invalid event
        """

        if (status != 'BUSY' and status != 'AWAY' and status != 'ACTIVE'):
            client.socket.send(bytes('...INVALID STATUS\n', 'utf8'))
            client.socket.send(bytes('...POSSIBLE STATUS ARE: ACTIVE, AWAY, BUSY\n', 'utf8'))
            return

        for conn in self.clients:
            if (client != conn):
                conn.socket.send(bytes(client.name + ' ' + status +'\n', 'utf8'))

    def send_msg_to(self, author, addressee, msg):
        """
        Sends a message from the author to the addressee

        :param author: The author
        :param addressee: The addressee
        :param msg: The message
        """

        room = self.get_personal_room(author.id, addressee)
        if (room is None):
            author.socket.send(bytes("...USER "+ addressee+ " NOT FOUND\n", 'utf8'))
        else:
            content = author.name + ': ' + msg
            room.add_msg(content)
            author.socket.send(bytes("...MESSAGE SENT\n", 'utf8'))
            ad_conn = self.get_client_by_name(addressee)
            ad_conn.socket.send(bytes(content+"\n", 'utf8'))

    def send_msg_to_all(self, author, msg):
        """
        Sends a message from an author to everyone

        :param author: The author
        :param msg: The message
        """

        room = self.lobbies[0]
        content = author.name + ': ' + msg
        room.add_msg(content)
        for conn in self.clients:
            if (author != conn):
                conn.socket.send(bytes('...PUBLIC-'+content+'\n', 'utf8'))

    def send_msg_to_room(self, room_name, author, msg):
        """
        Sends a message to an existant room, otherwise it tells the client that room does not exists or
        that he isn't invited.

        :param room_name: The room's name
        :param author: The author
        :param msg: The message
        :return: None if the client is or isn't in the room
        """

        for lobby in self.lobbies:
            if (lobby.name == room_name):
                if (author.id in lobby.accepted_clients):
                    content = author.name + ': ' + msg
                    lobby.add_msg(content)
                    for conn in self.clients:
                        if (conn.id in lobby.accepted_clients):
                            if (conn.id == author.id):
                                author.socket.send(bytes("...MESSAGE SENT\n", 'utf8'))
                            else:
                                conn.socket.send(bytes('...'+ room_name +'-'+content+'\n', 'utf8'))
                else:
                    author.socket.send(bytes("...YOU ARE NOT PART OF THE ROOM\n", 'utf8'))
                return

        author.socket.send(bytes("...ROOM NOT EXISTS", 'utf8'))


    def create_room(self, name, owner):
        """
        Creates a room with a name and an owner

        :param name: The room's name
        :param owner: The room's owner
        """

        for lobby in self.lobbies:
            if (lobby.name == name):
                owner.socket.send(bytes('...ROOM '+ name +' ALREADY IN USE\n', 'utf8'))
                return

        r = Room(name = name, owner = owner.id, invited = [owner.id, ])
        r.accept_guest(owner.id)
        self.lobbies.append(r)
        owner.socket.send(bytes('...ROOM CREATED\n', 'utf8'))

    def add_invitations(self, room_name, owner, invited):
        """
        Adds invitations to a room and notifies the clients that they were invited to the room.

        :param room_name: The room's name
        :param owner: The room's owner
        :param invited: A list of invited connections
        """

        room = self.get_room(owner.id, room_name)

        if (room == None):
            for lobby in self.lobbies:
                if (lobby.name == room_name and lobby.owner != owner.id):
                    owner.socket.send(bytes('...YOU ARE NOT OWNER OF THE ROOM\n', 'utf8'))
                    return

            owner.socket.send(bytes('...ROOM NOT EXISTS\n', 'utf8'))
            return

        for username in invited:
            user = self.get_client_by_name(username)
            if (user != None):
                room.add_invitation(user.id)
                user.invitations.append((owner.id, room.name))
                msg_invitation = []
                msg_invitation.append('...INVITATION TO JOIN '+ room_name +' ROOM BY '+ owner.name +'\n')
                msg_invitation.append('...TO JOIN: JOINROOM '+ room_name +'\n')
                content = ''.join(msg_invitation)
                user.socket.send(bytes(content, 'utf8'))
                owner.socket.send(bytes('...INVITATION SENT TO ' + user.name + '\n', 'utf8'))


    def join_room(self, client, room_name):
        """
        The client joins the room with the given name

        :param client: The client
        :param room_name: The room's name
        """

        found = False
        for lobby in self.lobbies:
            if (lobby.name == room_name):
                found = True
                i = 0
                for owner, r_name in client.invitations:
                    if (lobby.owner == owner):
                        lobby.accept_guest(client.id)
                        del client.invitations[i]
                        client.socket.send(bytes('...SUCCESFULLY JOINED TO ROOM\n', 'utf8'))
                        return
                    i += 1
        if (not found):
            client.socket.send(bytes('...ROOM NOT EXISTS\n', 'utf8'))
        else:
            client.socket.send(bytes('...YOU ARE NOT INVITED TO ROOM '+ room_name +'\n', 'utf8'))


    def disconnect_client(self, client):
        """
        Disconnects a connection from the server, deleting the rooms he was owner of and the private
        conversations.

        :param client: The client to disconnect
        """

        try:
            client.socket.send(bytes("You're now logged off", 'utf8'))
            client.socket.close()
        except SocketError as err:
            pass

        self.clients.remove(client)
        global_room = self.lobbies[0]
        global_room.accepted_clients = [id for id in global_room.accepted_clients if id != client.id]

        for lobby in self.lobbies[:]:
            if (lobby.type == 'personal'):
                if (client.id in lobby.accepted_clients):
                    self.lobbies.remove(lobby)
            else:
                if (lobby.owner != client.id):
                    lobby.accepted_clients = [id for id in lobby.accepted_clients if id != client.id]
                else:
                    self.lobbies.remove(lobby)

        if (self.mode != 'unittest'):
            print('User {} has disconnected'.format(client.name))
        self.send_msg_to_all(self.server_conection, 'User {} has disconnected'.format(client.name))

    def handle_event(self, client, msg):
        """
        Handles the event that a client send.

        :param client: The client
        :param msg: The message sent
        """

        try:
            event = Event.get_event(msg)
            instructions = msg.split()

            if (event == Event.IDENTIFY):
                if (len(instructions) == 2):
                    self.identify_client(client, instructions[1])
                else:
                    self.invalid_event(client)
                return

            elif (event == Event.DISCONNECT):
                self.disconnect_client(client)
                return

            elif (event == Event.INVALID):
                self.invalid_event(client)
                return

            if (not client.has_identified and self.mode != 'unittest'):
                self.must_identify(client)
                return

            if (event == Event.USERS):
                if (len(instructions) == 1):
                    self.users(client)
                else:
                    self.invalid_event(client)

            if (event == Event.STATUS):
                if (len(instructions) == 2):
                    self.send_status(client, instructions[1])
                else:
                    self.invalid_event(client)

            elif (event == Event.MESSAGE):
                if (len(instructions) > 2):
                    addressee = instructions[1]
                    content = ' '.join([instructions[x] for x in range(2, len(instructions))])
                    self.send_msg_to(client, addressee, content)
                else:
                    self.invalid_event(client)

            elif (event == Event.PUBLICMESSAGE):
                if (len(instructions) > 1):
                    content = ' '.join([instructions[x] for x in range(1, len(instructions))])
                    self.send_msg_to_all(client, content)
                else:
                    self.invalid_event(client)

            elif (event == Event.CREATEROOM):
                if (len(instructions) > 1):
                    name = instructions[1]
                    self.create_room(name, client)
                else:
                    self.invalid_event(client)

            elif (event == Event.INVITE):
                if (len(instructions) > 2):
                    name = instructions[1]
                    self.add_invitations(name, client, [instructions[i] for i in range(2, len(instructions))])
                else:
                    self.invalid_event(client)

            elif (event == Event.JOINROOM):
                if (len(instructions) == 2):
                    room_name = instructions[1]
                    self.join_room(client, room_name)
                else:
                    self.invalid_event(client)

            elif (event == Event.ROOMESSAGE):
                if (len(instructions) > 2):
                    room_name = instructions[1]
                    content = ' '.join([instructions[x] for x in range(2, len(instructions))])
                    self.send_msg_to_room(room_name, client, content)
                else:
                    self.invalid_event(client)

        except:
            pass

    def check_client(self, client):
        """
        Tests whether or not the client is still connected.

        :param client: The client
        """

        try:
            client.socket.send(bytes('...THIS MSG IS GENERATED, DO NOT WORRY'))
        except Exception as e:
            if (client in self.clients):
                self.disconnect_client(client)

    def handle_client(self, client):
        """
        Handles the actions a connection can do

        :param client: The connection
        """

        while True:
            try:

                msg = client.socket.recv(self.buffer_size).decode('utf8')
                if (not msg):
                    self.check_client(client)

                self.handle_event(client, msg)
                if (self.mode == 'debug'):
                    print('Rooms: ' + str(self.print_rooms()))
                    print('Users: ' + str(self.print_users()))

            except SocketError as e:
                if (self.mode != 'unittest'):
                    print(e)
                if (client in self.clients):
                    self.disconnect_client(client)
                break

    def establish_communication(self, client):
        """
        Once a connection is accepted, a private room is created for each of the clients that are connected
        to the server, and the connection is added to the public room.

        :param client: The new connection
        """

        for lobby in self.lobbies:
            if (lobby.name == 'PUBLIC'):
                lobby.add_invitation(client.id)
                lobby.accept_guest(client.id)

        for conn in self.clients:
            r = Room(name = conn.name, owner = client.id, invited = [conn.id, ], type = 'personal')
            r.accept_guest(conn.id)
            self.lobbies.append(r)

    def print_rooms(self):
        """
        USE FOR DEBUG ONLY
        Returns the available rooms in the server.

        :return: the available rooms in the server.
        """

        l = []
        for lobby in self.lobbies:
            name = lobby.name
            owner = lobby.owner
            invited = lobby.invited_clients
            accepted = lobby.accepted_clients
            msgs = lobby.msg_list
            l.append((name, owner, invited, accepted, msgs))
        return l

    def print_users(self):
        """
        USE FOR DEBUG ONLY
        Returns the available users in the server.

        :return: the available connections in the server.
        """

        l = []
        for conn in self.clients:
            l.append((conn.id, conn.name, conn.invitations))
        return l


    def accept_conections(self):
        """
        Accepts the connections that the server receives.
        """

        if (self.mode != 'unittest'):
            print('Waiting for connections...')
        while (self.is_on):
            try:
                client_socket, client_address = self.server.accept()
                if (self.mode != 'unittest'):
                    print('{} has connected'.format(client_address))
                client = self.create_new_conection(client_address[1], client_address[1], client_socket)
                self.clients.append(client)
                self.establish_communication(client)
                Thread( target = self.handle_client, args=(client,), daemon=True).start()
            except Exception as e:
                if (self.mode != 'unittest'):
                    print(e)
                self.close()
                break
