import unittest
import sys
import random
from time import sleep
from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
from ..Client import Client

class TestConection(unittest.TestCase):

    def handle_client(self, client):
        while True:
            type = client.socket.recv(self.buffer_size).decode('utf8')

            if (type == 'no one'):
                client.socket.close()
                break

            msg = client.socket.recv(self.buffer_size).decode('utf8')
            if (type == 'all'):
                for addressee in self.server_clients:
                    addressee.socket.send(bytes(prefix + msg).encode('utf8'))
            else:
                addressee = self.server_clients[type]
                addressee.socket.send(bytes(prefix + msg).encode('utf8'))

    def runnable(self):
        print('Waiting for connections...')

        while True:

            if (self.server_status == 0):
                print('The server is now closed')
                self.server.close()
                break

            try:
                client_socket, client_address = self.server.accept()
                client = Client(client_socket, client_name, client_address)
                self.server_counter += 1
                print('A client has connected')
                client_thread = Thread(target=handle_client, args=(client,))
                client_thread.daemon = True
                client_thread.start()

            except Exception as e:
                print(e)
                self.assertTrue(False)


    def set_up_server(self):
        self.host = 'localhost'
        self.port = 33000
        self.buffer_size = 1024
        self.address = (self.host, self.port)
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        try:
            self.server.bind(self.address)
            self.server.listen(0)
            self.server_status = 1
            self.server_thread = Thread(target = self.runnable)
            self.server_thread.daemon = True
            self.server_thread.start()
        except Exception as e:
            print('Failed to set up server.')
            self.assertTrue(server_status)

    def client_connection(self):
        self.server_clients = {}
        s = socket()
        client_1 = Client(s, '...', 'Marco')
        client_1.connect('localhost', 33000)
        self.server_clients['Marco'] = client_1
        self.assertTrue(client_1.is_connected())
        s = socket()
        client_2 = Client(s, '...', 'Polo')
        self.server_clients['Polo'] = client_2
        self.assertTrue(client_2.is_connected())
        s = socket()
        client_3 = Client(s, '...', 'Arthur')
        self.server_clients['Arthur'] = client_3
        self.assertTrue(client_3.is_connected())
        client_1.send_msg_to('Hello', 'Polo')
        msg_list_1 = client_2.get_msg_list_of('Marco')
        self.assertTrue('Hello' in msg_list_1)
        client_2.send_msg_to_all('Hello everyone')
        msg_list_2 = client_1.get_msg_list_of('All')
        msg_list_3 = client_3.get_msg_list_of('All')
        self.assertTrue('Hello everyone' in msg_list_2)
        self.assertTrue('Hello everyone' in msg_list_3)
        client_1.disconnect()
        client_2.disconnect()
        client_3.disconnect()
        self.assertFalse(client_1.is_connected())
        self.assertFalse(client_2.is_connected())
        self.assertFalse(client_3.is_connected())


    def test_client(self):
        self.set_up_server()
        sleep(1)
        self.client_connection()
        sleep(1)
        self.server_status = 0
        self.server_thread.join()

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestConection)

    unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
