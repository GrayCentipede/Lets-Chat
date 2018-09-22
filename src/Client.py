from socket import socket
from socket import error as SocketError
from time import sleep
import sys

from .ClientStatus import ClientStatus

"""
A class for the client.
To generate HTML documentation for this module use the command:

    pydoc -w src.Client
    
"""

class Client(object):
    """
    Client will be able to connect to a server and talk to it.
    It encapsulates:
        buffer_size - The size of the buffer
        socket - The socket to user for communication
        name - The client's name
        is_connected - Tells if the client is connected to a sever.
        status - The client's status
        log - The log of messages the server returns
        listener - A listener
    """

    buffer_size = 1024
    socket = None
    name = None
    is_connected = False
    status = None
    log = None
    listener = None

    def __init__(self, name, address = ''):
        """
        Constructs a client

        :param name: The name of the client
        :param address: The client's address
        """

        self.socket = socket()
        self.name = name
        self.log = []

    def set_address(self, address):
        """
        Sets the client's address

        :param address: The address to set
        """

        self.address = address

    def set_name(self, name):
        """
        Sets the client's name

        :param name: The name to set
        """

        self.name = name

    def get_name(self):
        """
        Returns the client's name.

        :return: Returns the name
        """
        return self.name

    def set_listener(self, f):
        """
        Sets the client's listener

        :param name: The functions that will be the listener
        """

        self.listener = f

    def connect(self, host, port):
        """
        The client connects to the given host and port.

        :param host: The server's host
        :param port: The server's port
        :raises SocketError: If the client fails to connect the server it raises an exception
        """

        try:
            self.socket.connect((host, port))
            self.is_connected = True
            self.status = ClientStatus.ACTIVE
        except Exception as e:
            raise SocketError(e)

    def disconnect(self):
        """
        The client disconnects from the server.

        :raises SocketError: If fails to disconnect.
        """

        try:
            self.socket.close()
            self.is_connected = False
        except Exception as e:
            raise SocketError(e)

    def is_online(self):
        """
        Returns if the client is connected to a server.

        :return: True if it is connected, false otherwise.
        """

        return self.is_connected

    def get_status(self):
        """
        Returns the client's status

        :return: The client's status.
        """

        return self.status

    def receive_from_server(self):
        """
        While the msg is not None and the client is connected it will try to read whatever the server sends.
        Then it will pass the msg to the listener and append it to its log.
        """

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
        """
        Returns the log.

        :return: The log
        """
        return self.log

    def send_msg(self, msg):
        """
        Sends a msg to the server. If the message is a command to update the client's status then it will be
        updated, as well as if it identifies itself or if it will disconnect.

        :param msg: The message to send
        :raises SocketError: In case the communication between the server and the client fails.
        """

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
