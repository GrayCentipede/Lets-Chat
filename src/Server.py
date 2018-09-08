from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
import signal

from .Client import Client
from .Room import Room

class Server(object):
    buffer_size = 1024
    host = None
    port = None
    server = None
    lobbies = {}
    clients = {}
    server_id = '.-.'
    is_on = 0

    class Conection(object):
        name = None
        address = None
        socket = None

        def __init__(self, name, address, socket):
            self.name = name
            self.address = address
            self.socket = socket


    def __init__(self, port, host = 'localhost', num_conections = 10):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

        try:
            self.server.bind(self.address)
            self.server.listen(num_conections)
            self.lobbies['global'] = Room('global')
            self.is_on = 1
            print('Server {} is now awaiting for connections at port {}'.format(host, port))

        except Exception as e:
            print('An error has occurred while trying to lift the server: ' + str(e))

    def close(self):
        print('Shutting down server {}'.format(self.host))
        self.send_msg_to_all(self.server_id, 'The server {} is shutting down. Thanks for staying.'.format(self.host))
        self.server_status = 0
        copy = self.clients.copy()
        for address in copy:
            client = self.clients[address]
            self.disconnect_client(client)

    def send_msg_to(self, author, addressee, msg):
        is_server = False
        client = None

        if (str(author) == self.server_id):
            prefix = '@' + self.server_id + ' : '
            addressee.socket.send(bytes(prefix + msg, 'utf8'))
            return

        prefix = '@' + author.name + ' : '

        for address in self.clients:
            client = self.clients[address]
            if (client.name == addressee):
                break

        if (not is_server) and (author.address != client.address):
            author.socket.send(bytes(prefix + msg, 'utf8'))

        client.socket.send(bytes(prefix + msg, 'utf8'))

    def send_msg_to_all(self, author, msg):
        if (str(author) == self.server_id):
            prefix = '@' + self.server_id + ' : '
        else:
            prefix = '@' + author.name + ' :'
        for address in self.clients:
            client = self.clients[address]
            client.socket.send(bytes(prefix + msg, 'utf8'))

    def disconnect_client(self, client):
        try:
            client.socket.send((bytes('Goodbye', 'utf8')))
            client.socket.close()
        except:
            pass
        finally:
            del self.clients[client.address]
            self.send_msg_to_all('.-.', 'User {} has disconnected.'.format(client.name))
            print('{} has disconnected'.format(client.address))

    def handle_client(self, client):
        try:
            client.name = client.socket.recv(self.buffer_size).decode('utf8')
            self.lobbies[client.address] = Room(client.name)
            greetings = """ Welcome {}.
                            You're now connected to {}.
                            If you ever want to quit, type: 'no one' when you're asked with who do you want to
                            talk to exit the chat.
                        """.format(client.name, self.host)
            self.send_msg_to(self.server_id, client, greetings)

            while True:
                addressee = client.socket.recv(self.buffer_size).decode('utf8')

                if (addressee == 'no one'):
                    self.disconnect_client(client)
                    break

                msg = client.socket.recv(self.buffer_size).decode('utf8')

                if (addressee != 'to_all'):
                    self.send_msg_to(client, addressee, msg)
                else:
                    self.send_msg_to_all(client, msg)
        except Exception as e:
            print(e)
            self.disconnect_client(client)

    def accept_conections(self):
        print('Waiting for connections...')
        while (self.is_on):
            try:
                client_socket, client_address = self.server.accept()
                print('{} has connected'.format(client_address))
                client = self.Conection('', client_address[1], client_socket)
                self.clients[client_address[1]] = client
                Thread( target = self.handle_client, args=(client,), daemon=True).start()
            except Exception:
                self.close()
                break
