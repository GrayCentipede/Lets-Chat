from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from socket import error as SocketError
from threading import Thread
import signal

from .Event import Event
from .Room import Room

class Server(object):
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
        id = 0
        name = None
        address = None
        socket = None
        invitations = None
        has_identified = False

        def __init__(self, id, name, address, socket):
            self.id = id
            self.name = name
            self.address = address
            self.socket = socket
            self.invitations = []

    def create_new_conection(self, name, address, socket):
        connection = self.Connection(self.id_autoincrement, name, address, socket)
        self.id_autoincrement += 1
        return connection

    def __init__(self, port, host = 'localhost', num_conections = 10, mode = 'normal'):
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
        if (self.mode != 'unittest'):
            print('Shutting down server {}'.format(self.host))
        self.send_msg_to_all(self.server_conection, 'The server {} is shutting down. Thanks for staying.'.format(self.host))
        self.server_status = 0
        copy = self.clients.copy()
        for client in copy:
            self.disconnect_client(client)

        self.server.close()

    def get_client_by_name(self, name):
        for conn in self.clients:
            if (conn.name == name):
                return conn

        return None

    def invalid_event(self, client, num_args):
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
        msg ='...MUST IDENTIFY FIRST\n...TO IDENTIFY: IDENTIFY USERNAMER\n'
        client.socket.send(bytes(msg, 'utf8'))

    def identify_client(self, client, name):
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
        user_list = ' '.join([conn.name for conn in self.clients])
        client.socket.send(bytes(user_list + '\n', 'utf8'))

    def get_personal_room(self, author_id, addressee_name):
        addressee = self.get_client_by_name(addressee_name)
        for lobby in self.lobbies:
            if (lobby.type == 'personal'):
                a = (lobby.owner == author_id and addressee.id in lobby.accepted_clients)
                b = (lobby.owner == addressee.id and author_id in lobby.accepted_clients)
                if (a or b):
                    return lobby

        return None

    def get_room(self, owner_id, name):
        for lobby in self.lobbies:
            if (lobby.owner == owner_id and lobby.name == name):
                return lobby

        return None

    def send_msg_to(self, author, addressee, msg):
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
        room = self.lobbies[0]
        content = author.name + ': ' + msg
        room.add_msg(content)
        for conn in self.clients:
            if (author != conn):
                conn.socket.send(bytes('...PUBLIC-'+content+'\n', 'utf8'))

    def send_msg_to_room(self, room_name, author, msg):
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
        for lobby in self.lobbies:
            if (lobby.name == name):
                owner.socket.send(bytes('...ROOM '+ name +' ALREADY IN USE\n', 'utf8'))
                return

        r = Room(name = name, owner = owner.id, invited = [owner.id, ])
        r.accept_guest(owner.id)
        self.lobbies.append(r)
        owner.socket.send(bytes('...ROOM CREATED\n', 'utf8'))

    def add_invitations(self, room_name, owner, invited):
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
        try:
            event = Event.get_event(msg)
            instructions = msg.split()

            if (event == Event.IDENTIFY):
                if (len(instructions) == 2):
                    self.identify_client(client, instructions[1])
                else:
                    self.invalid_event(client, 2)
                return

            elif (event == Event.DISCONNECT):
                self.disconnect_client(client)
                return

            elif (event == Event.INVALID):
                self.invalid_event(client, 0)
                return

            if (not client.has_identified and self.mode != 'unittest'):
                self.must_identify(client)
                return

            if (event == Event.USERS):
                if (len(instructions) == 1):
                    self.users(client)
                else:
                    self.invalid_event(client, 1)

            elif (event == Event.MESSAGE):
                if (len(instructions) > 2):
                    addressee = instructions[1]
                    content = ' '.join([instructions[x] for x in range(2, len(instructions))])
                    self.send_msg_to(client, addressee, content)
                else:
                    self.invalid_event(client, 3)

            elif (event == Event.PUBLICMESSAGE):
                if (len(instructions) > 1):
                    content = ' '.join([instructions[x] for x in range(1, len(instructions))])
                    self.send_msg_to_all(client, content)
                else:
                    self.invalid_event(client, 2)

            elif (event == Event.CREATEROOM):
                if (len(instructions) > 1):
                    name = instructions[1]
                    self.create_room(name, client)
                else:
                    self.invalid_event(client, 2)

            elif (event == Event.INVITE):
                if (len(instructions) > 2):
                    name = instructions[1]
                    self.add_invitations(name, client, [instructions[i] for i in range(2, len(instructions))])
                else:
                    self.invalid_event(client, 2)

            elif (event == Event.JOINROOM):
                if (len(instructions) == 2):
                    room_name = instructions[1]
                    self.join_room(client, room_name)
                else:
                    self.invalid_event(client, 2)

            elif (event == Event.ROOMESSAGE):
                if (len(instructions) > 2):
                    room_name = instructions[1]
                    content = ' '.join([instructions[x] for x in range(2, len(instructions))])
                    self.send_msg_to_room(room_name, client, content)
                else:
                    self.invalid_event(client, 2)

        except:
            pass

    def check_client(self, client):
        try:
            client.socket.send(bytes('...THIS MSG IS GENERATED, DO NOT WORRY'))
        except Exception as e:
            if (client in self.clients):
                self.disconnect_client(client)

    def handle_client(self, client):
        while True:
            try:

                msg = client.socket.recv(self.buffer_size).decode('utf8')
                if (not msg):
                    self.check_client(client)

                self.handle_event(client, msg)
                if (self.mode != 'unittest'):
                    print('Rooms: ' + str(self.print_rooms()))
                    print('Users: ' + str(self.print_users()))

            except SocketError as e:
                if (self.mode != 'unittest'):
                    print(e)
                if (client in self.clients):
                    self.disconnect_client(client)
                break

    def establish_communication(self, client):
        for lobby in self.lobbies:
            if (lobby.name == 'PUBLIC'):
                lobby.add_invitation(client.id)
                lobby.accept_guest(client.id)

        for conn in self.clients:
            r = Room(name = conn.name, owner = client.id, invited = [conn.id, ], type = 'personal')
            r.accept_guest(conn.id)
            self.lobbies.append(r)

    def print_rooms(self):
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
        l = []
        for conn in self.clients:
            l.append((conn.id, conn.name, conn.invitations))
        return l


    def accept_conections(self):
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
