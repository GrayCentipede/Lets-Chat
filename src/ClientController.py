from .Client import Client
from threading import Thread

"""
A class for the client's controller.
To generate HTML documentation for this module use the command:

    pydoc -w src.ClientController
    
"""

class ClientController(object):
    """
    The ClientController will return the client's propierties and it updates
    the users interface depending on the client's status.
    It encapsulates:
        client = The client object.
        client_communication = The thread of the client so that it can receive the server messages.
        instancer = The app that instanced it.
    """

    client = None
    client_communication = None
    instancer = None

    def __init__(self, instancer):
        """
        Constructs a client's controller that has a client object.

        :param instancer: The app that instanced it.
        """

        self.client = Client('YET TO IDENTIFY')
        self.instancer = instancer

    def connect_client(self, host, port):
        """
        It connects the client to the given host and port.

        :param host: The host to connect to.
        :param port: The port where the conection will be made.
        """

        self.client.connect(host, port)
        self.client_communication = Thread(target = self.client.receive_from_server, daemon = True)
        self.client_communication.start()

    def client_is_connected(self):
        """
        Returns if the client is online, in other words, is connected to a server.

        :return: True if is online, false otherwise.
        """

        return self.client.is_online()

    def get_client_status(self):
        """
        Returns the client's status

        :return: The client's status
        """

        return self.client.get_status()

    def get_client_name(self):
        """
        Returns the client's name

        :return: The client's name
        """

        return self.client.get_name()

    def disconnect_client(self):
        """
        Disconnects the client.
        """

        self.client.disconnect()

    def send_msg(self, msg):
        """
        Tells the client to send a message.

        :param msg: The message to send.
        """

        self.client.send_msg(msg)

    def set_client_listener(self):
        """
        Sets the client's listener to update the chat room in the app.
        """

        self.client.set_listener(lambda msg: self.instancer.chat_room.append_msg(msg))
