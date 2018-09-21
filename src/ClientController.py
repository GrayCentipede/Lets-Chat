from .Client import Client
from threading import Thread

class ClientController(object):

    client = None
    client_communication = None
    instancer = None

    def __init__(self, instancer):
        self.client = Client('YET TO IDENTIFY')
        self.instancer = instancer

    def connect_client(self, host, port):
        self.client.connect(host, port)
        self.client_communication = Thread(target = self.client.receive_from_server, daemon = True)
        self.client_communication.start()

    def client_is_connected(self):
        return self.client.is_online()

    def get_client_name(self):
        return self.client.get_name()

    def disconnect_client(self):
        self.client.disconnect()

    def send_msg(self, msg):
        self.client.send_msg(msg)

    def set_client_listener(self):
        self.client.set_listener(lambda msg: self.instancer.chat_room.append_msg(msg))
