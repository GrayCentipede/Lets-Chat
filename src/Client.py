from socket import socket
import sys

class Client(object):

    msg_list = {}
    buffer_size = 1024
    socket = None
    name = None
    is_connected = False

    def __init__(self, name, address = ''):
        self.socket = socket()
        self.name = name

    def set_address(self, address):
        self.address = address

    def set_name(self, name):
        self.name = name

    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
            self.socket.send(bytes(self.name))
            self.is_connected = True
        except Exception as e:
            print('Failed to connect {}'.format(host))
            sys.exit()

    def disconnect(self):
        try:
            self.socket.close()
            self.is_connected = False
            print('The conection between the server and you has been closed.')
        except Exception as e:
            print(e)

    def is_connected(self):
        return self.is_connected

    def receive_from_server(self):
        msg = '...'
        while True:
            try:
                if (self.is_connected) and (msg):
                    msg = self.socket.recv(self.buffer_size).decode('utf8')
                    print(msg)
                else:
                    break
            except Exception as e:
                print('Exception occurred on receive')
        if (self.is_connected):
            self.disconnect()

    def send_msg(self):
        while self.is_connected:
            try:
                addressee = raw_input('Who do you wanna talk with? ').strip()

                if (addressee == 'no one'):
                    self.socket.send(bytes(addressee).encode('utf8'))
                    self.disconnect()
                    break

                msg = raw_input('Write something cute: ').strip()
                self.send_msg_to(addressee, msg)
            except Exception as e:
                print('A conection error occurred, you are no longer connected to the server')

    def send_msg_to(self, addressee, msg):
        self.socket.send(bytes(addressee).encode('utf8'))
        self.socket.send(bytes(msg).encode('utf8'))
