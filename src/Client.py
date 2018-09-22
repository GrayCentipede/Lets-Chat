from socket import socket
from socket import error as SocketError
from time import sleep
import sys

from .ClientStatus import ClientStatus

class Client(object):

    buffer_size = 1024
    socket = None
    name = None
    is_connected = False
    status = None
    log = None
    listener = None

    def __init__(self, name, address = ''):
        self.socket = socket()
        self.name = name
        self.log = []

    def set_address(self, address):
        self.address = address

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_listener(self, f):
        self.listener = f

    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
            self.is_connected = True
            self.status = ClientStatus.ACTIVE
        except Exception as e:
            raise SocketError(e)

    def disconnect(self):
        try:
            self.socket.close()
            self.is_connected = False
        except Exception as e:
            raise SocketError(e)

    def is_online(self):
        return self.is_connected

    def get_status(self):
        return self.status

    def receive_from_server(self):
        msg = "..."
        while True:
            try:
                if (self.is_connected) and (msg):
                    msg = self.socket.recv(self.buffer_size).decode('utf8')
                    self.log.append(msg)
                    self.listener(msg)
                else:
                    break
            except Exception as e:
                self.log.append(str(e))
                break
        if (self.is_connected):
            self.disconnect()

    def get_last_msgs(self):
        return self.log

    def send_msg(self, msg):
        try:
            if (len(msg) > 0):
                instructions = msg.split()
                if ('STATUS' == instructions[0]):
                    if (len(instructions) <= 2):
                        if (instructions[1] == 'ACTIVE'):
                            self.status = ClientStatus.ACTIVE
                        elif (instructions[1] == 'BUSY'):
                            self.status = ClientStatus.BUSY
                        elif (instructions[1] == 'AWAY'):
                            self.status = ClientStatus.AWAY
                        else:
                            print('Invalid argument.')

                    else:
                        print('Invalid argument')

                if (instructions[0] == 'IDENTIFY'):
                    self.name = instructions[1]

                self.socket.send(bytes(msg.strip() + '\n', 'utf8'))

                if (msg == 'DISCONNECT'):
                    self.disconnect()

        except Exception as e:
            raise SocketError(e)
