import unittest
import sys
import random
from time import sleep
from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
from ..Client import Client

class TestConection(unittest.TestCase):

    class Conection(object):

        def __init__(self, cl_socket, cl_address):
            self.c_socket = cl_socket
            self.c_address = cl_address

    def handle_client(self, client):
        while True:
            msg = client.socket.recv(self.buffer_size).decode('utf8')

            instructions = msg.split()
            event = instructions[0]

            if (event == 'IDENTIFY'):
                new_name = instructions[1]
                c = self.clients[client.c_address]
                self.clients[new_name] = c
                del self.clients[client.c_address]

            elif (event == 'MESSAGE'):
                addressee = instructions[1]
                content = ' '.join(instructions[i] for i in range(2, len(instructions)))
                addressee_conection = self.clients[addressee]
                addressee_conection.c_socket.send(bytes(content, 'utf8'))

            elif (event == 'DISCONNECT'):
                del self.clients[client.c_address]
                self.server_counter -= 1
                client.c_socket.close()

    def runnable(self):

        while True:

            if (self.server_status == 0):
                self.server.close()
                break

            try:
                client_socket, client_address = self.server.accept()
                client = self.Conection(client_socket, client_address[1])
                self.clients[client_address] = client
                self.server_counter += 1
                client_thread = Thread(target = self.handle_client, args=(client,))
                client_thread.daemon = True
                client_thread.start()

            except Exception as e:
                print(e)
                self.assertTrue(False)

    def setUp(self):
        self.host = 'localhost'
        self.port = 33000
        self.buffer_size = 1024
        self.address = (self.host, self.port)
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        try:
            self.server.bind(self.address)
            self.server.listen(10)
            self.server_status = 1
            self.server_counter = 0
            self.clients = {}
            self.server_thread = Thread(target = self.runnable)
            self.server_thread.daemon = True
            self.server_thread.start()
            sleep(0.5)
        except Exception as e:
            print('Failed to set up server.')
            self.assertTrue(server_status)

    def test_client_is_connected(self):
        client_1 = Client(name = 'Marco', address = 'localhost')
        client_1.connect(self.host, self.port)
        self.assertTrue(client_1.is_connected())
        self.assertEqual(self.server_counter, 1)

    def test_client_send_msg(self):
        self.server_counter = 0
        client_1 = Client(name = 'Marco', address = 'localhost')
        client_1.connect(self.host, self.port)
        client_1.send_msg('IDENTIFY Polo')
        self.assertEqual(client_1.get_name(), 'Polo')
        client_2 = Client(name = 'Polo', address = 'localhost')
        client_1.send_msg('MESSAGE Polo Hello Polo')
        self.assertTrue('Hello Polo' in client_2.get_last_msgs())

    def test_client_disconnect(self):
        self.server_counter = 0
        client_1 = Client(name = 'Marco', address = 'localhost')
        client_1.connect(self.host, self.port)
        self.assertEqual(self.server_counter, 1)
        client_1.send_msg('DISCONNECT')
        self.assertFalse(client_1.is_connected())
        self.assertEqual(self.server_counter, 0)

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestConection)

    unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
