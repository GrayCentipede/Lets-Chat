from socket import socket
import sys

from .ClientStatus import ClientStatus

class Client(object):

    buffer_size = 1024
    socket = None
    name = None
    is_connected = False
    status = None

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
            self.socket.send(bytes(self.name, 'utf8'))
            self.is_connected = True
        except Exception as e:
            print(e)
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
                break
        if (self.is_connected):
            self.disconnect()

    def send_msg(self):
        while self.is_connected:
            try:
                msg = input('Write something cute: \n').strip()

                if (len(msg) > 0):
                    instructions = msg.split()
                    if ('STATUS' == instructions[0]):
                        if (len(instructions) <= 2):
                            if (s[1] == 'ACTIVE'):
                                self.status = ClientStatus.ACTIVE
                            elif (s[1] == 'BUSY'):
                                self.status = ClientStatus.BUSY
                            elif (s[1] == 'AWAY'):
                                self.status = ClientStatus.AWAY
                            else:
                                print('Invalid argument.')

                        else:
                            print('Invalid argument')

                    self.socket.send(bytes(msg, 'utf8'))

                    if (msg == 'DISCONNECT'):
                        self.disconnect()
                        break

            except Exception as e:
                print(e)
                print('A conection error occurred, you are no longer connected to the server')
                break
