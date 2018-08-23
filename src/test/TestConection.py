import unittest
import random
from time import sleep
from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
from ..Client import Client

class TestConection(unittest.TestCase):

    def runnable(self):

        while True:

            if (self.server_status == 0):
                print('The server is now closed')
                self.server.close()
                break

            try:
                print('Waiting for connections')
                client_socket, client_address = self.server.accept()
                self.server_counter += 1
                print('A client has connected')
                client_status = 1
                while client_status == 1:
                    client_socket.close()
                    self.server_counter -= 1
                    print('The client is no longer in the server')
                    client_status = 0


            except Exception as e:
                pass


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
            self.server_counter = 0
        except:
            print('Localhost is already in use, close the terminal and run the test again.')
            self.assertTrue(False)

        try:
            self.server_thread = Thread(target = self.runnable)
            self.server_thread.start()
        except:
            self.assertTrue(False)


    def test_client(self):
        self.set_up_server()
        sleep(1)
        s = socket()
        s.connect(('localhost', self.port))
        while True:
            if self.server_counter >= 1:
                continue
            else:
                self.server_status = 0
                break

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestConection)

    unittest.TextTestRunner(verbosity=2).run(suite)
