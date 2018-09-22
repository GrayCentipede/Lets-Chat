import unittest
import sys
import random
from time import sleep
from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
from ..Client import Client

"""
Unit test to check whether or not the client can connect, disconnect, send and receive to and from the server.
To generate HTML documentation for this module use the command:

    pydoc -w src.test.TestConection

"""

class TestConection(unittest.TestCase):
    """
    TestConection contains the unit tests for the conections.
    """

    class Conection(object):
        """
        Conection is a disposable class that is used in the disposable server so that there can be a
        communication between the client and the server.
        """

        def __init__(self, cl_socket, cl_address):
            """
            Constructs the disposable conection.

            :param cl_socket: The client's socket
            :param cl_address: The client's address
            """

            self.c_socket = cl_socket
            self.c_address = cl_address

    set_up_done = False

    def handle_client(self, client):
        """
        Handles the events that can send the client.

        :param client: The client's connection object
        """
        while True:
            try:
                msg = client.c_socket.recv(self.buffer_size).decode('utf8')

                instructions = msg.split()
                if (len(instructions) > 0):
                    event = instructions[0]

                    if (event == 'IDENTIFY'):
                        new_name = instructions[1]
                        self.clients[new_name] = self.clients.pop(client.c_address)
                        client.c_address = new_name

                    elif (event == 'MESSAGE'):
                        addressee = instructions[1]
                        content = ' '.join(instructions[i] for i in range(2, len(instructions)))
                        addressee_conection = self.clients[addressee]
                        addressee_conection.c_socket.send(bytes(content, 'utf8'))

                    elif (event == 'DISCONNECT'):
                        del self.clients[client.c_address]
                        self.server_counter -= 1
                        client.c_socket.close()
            except:
                break

    def runnable(self):
        """
        Method that handles the connections between the server and the client.
        """
        while True:

            if (self.server_status == 0):
                self.server.close()
                break

            try:
                client_socket, client_address = self.server.accept()
                client = self.Conection(client_socket, client_address[1])
                self.clients[client_address[1]] = client
                self.server_counter += 1
                client_thread = Thread(target = self.handle_client, args=(client,))
                client_thread.daemon = True
                client_thread.start()

            except Exception as e:
                print(e)
                self.assertTrue(False)

    def setUp(self):
        """
        Creates a disposable server for all the unit tests.
        """

        self.host = 'localhost'
        self.port = 33000
        self.buffer_size = 1024
        self.address = (self.host, self.port)

        if (not TestConection.set_up_done):
            self.server = socket(AF_INET, SOCK_STREAM)
            self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            try:
                self.server.bind(self.address)
                TestConection.set_up_done = True
                self.server.listen(10)
                self.server_status = 1
                self.server_counter = 0
                self.clients = {}
                self.server_thread = Thread(target = self.runnable)
                self.server_thread.daemon = True
                self.server_thread.start()
                sleep(0.25)
            except Exception as e:
                print(e)
                print('Failed to set up server.')

    def test_client_connect_and_disconnect(self):
        """
        Tests if the client can connect and disconnect to and from the server.
        """

        client_1 = Client(name = 'Marco', address = 'localhost')
        client_1.connect(self.host, self.port)
        sleep(0.0005)
        self.assertTrue(client_1.is_online())
        self.assertEqual(self.server_counter, 1)
        sleep(0.0005)
        client_1.send_msg('DISCONNECT')
        sleep(0.0005)
        self.assertFalse(client_1.is_online())
        self.assertEqual(self.server_counter, 0)

    def test_client_send_and_recv_msg(self):
        """
        Tests if the client can send and receive messages to and from the server.
        """

        self.server_counter = 0
        client_2 = Client(name = 'Marco', address = 'localhost')
        client_2.connect(self.host, self.port)
        client_2.send_msg('IDENTIFY Polo')
        sleep(0.0005)
        self.assertEqual(client_2.get_name(), 'Polo')
        client_3 = Client(name = 'Arthur', address = 'localhost')
        client_3.connect(self.host, self.port)
        client_3.send_msg('IDENTIFY Lancelot')
        sleep(0.0005)
        client_3_listen = Thread(target = client_3.receive_from_server, daemon = True)
        client_3_listen.start()
        sleep(0.0005)
        client_2.send_msg('MESSAGE Lancelot Hello Lancelot')
        sleep(0.0005)
        self.assertTrue('Hello Lancelot' in client_3.get_last_msgs())

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestConection)

    unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
