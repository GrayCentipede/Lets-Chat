import unittest
from socket import socket, timeout
from threading import Thread
from ..Server import Server

class TestServer(unittest.TestCase):
    def accept_connections(self):
        try:
            self.server_thread = Thread(target=server.accept_conections)
            self.server_thread.daemon = True
            self.server_thread.start()
            sleep(1)
            self.client_1_socket = socket()
            self.client_1_socket.connect(('localhost', 33000))
            self.client_2_socket = socket()
            self.client_2_socket.connect(('localhost', 33000))
            self.client_3_socket = socket()
            self.client_3_socket.connect(('localhost', 33000))
            self.handle_client()

        except:
            assert False

    def handle_client(self):
        try:
            self.client_1_socket.send(bytes('Marco').encode('utf8'))
            self.client_2_socket.send(bytes('Polo').encode('utf8'))
            self.client_3_socket.send(bytes('Arthur').encode('utf8'))
            self.client_3_socket.send(bytes('no one').encode('utf8'))
            sleep(0.5)
            self.assertRaises(timeout, self.client_3_socket.send(bytes('Hello').encode('utf8')))
            self.send_msg_to()
        except:
            assert False

    def send_msg_to(self):
        try:
            self.client_1_socket.send(bytes('Polo').encode('utf8'))
            self.client_1_socket.send(bytes('Hello Polo').encode('utf8'))
            msg = self.client_2_socket.recv(1024).decode('utf8')
            self.assertEqual(msg, 'Hello Polo')
            self.client_2_socket.send(bytes('Marco').encode('utf8'))
            self.client_2_socket.send(bytes('Hello Marco').encode('utf8'))
            msg = self.client_1_socket.recv(1024).decode('utf8')
            self.assertEqual(msg, 'Hello Marco')
            self.send_msg_to_all()
        except:
            assert False

    def send_msg_to_all(self):
        try:
            self.client_4_socket = socket()
            self.client_4_socket.connect(('localhost', 33000))
            self.client_4_socket.send(bytes('Lancelot').encode('utf8'))
            self.client_4_socket.send(bytes('lobby').encode('utf8'))
            self.client_4_socket.send(bytes('For Britannia').encode('utf8'))
            msg_1 = self.client_1_socket.recv(1024).decode('utf8')
            msg_2 = self.client_2_socket.recv(1024).decode('utf8')
            self.assertEqual('For Britannia', msg_1)
            self.assertEqual(msg_1, msg_2)

        except:
            assert False

    def test_server(self):
        self.server = Server(host = 'localhost', port = 33000)
        self.accept_connections()


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)

    unittest.TextTestRunner(verbosity=2, failfast = True).run(suite)
