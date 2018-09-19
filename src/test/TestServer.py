import unittest
from socket import socket, timeout
from threading import Thread
from time import sleep
from ..Server import Server
import random

class TestServer(unittest.TestCase):

    def setUp(self):
        self.host = 'localhost'
        self.port = 30000 + random.randint(0, 20000)
        self.server = Server(host = self.host, port = self.port, mode = 'unittest')
        self.server_thread = Thread(target = self.server.accept_conections, daemon = True)
        self.server_thread.start()
        TestServer.set_up_done = True

    def test_accept_connection_and_disconnect(self):
        connection_1 = socket()
        connection_1.connect((self.host, self.port))
        connection_1.send(bytes('IDENTIFY Marco', 'utf8'))
        sleep(0.0005)
        client_list = self.server.clients
        conn = client_list[0]
        self.assertEqual(conn.name, 'Marco')
        connection_1.send(bytes('DISCONNECT', 'utf8'))
        sleep(0.0005)
        self.assertEqual(len(client_list), 0)
        self.server.close()
        sleep(0.0005)

    def test_public_msg(self):
        connection_2 = socket()
        connection_2.connect((self.host, self.port))
        connection_2.send(bytes('IDENTIFY Polo', 'utf8'))
        sleep(0.005)
        connection_2.send(bytes('PUBLICMESSAGE Hello everyone', 'utf8'))
        sleep(0.005)
        rooms = self.server.lobbies
        global_room = rooms[0]
        self.assertTrue('Polo: Hello everyone' in global_room.msg_list)
        connection_2.send(bytes('DISCONNECT', 'utf8'))
        sleep(0.005)
        self.server.close()

    def test_private_msg(self):
        connection_3 = socket()
        connection_4 = socket()
        connection_3.connect((self.host, self.port))
        connection_4.connect((self.host, self.port))
        connection_3.send(bytes('IDENTIFY Bones', 'utf8'))
        connection_4.send(bytes('IDENTIFY Jelly', 'utf8'))
        sleep(0.005)
        connection_4.send(bytes('MESSAGE Bones TromBONE', 'utf8'))
        sleep(0.005)
        private_room = self.server.lobbies[2]
        self.assertTrue('Jelly: TromBONE' in private_room.msg_list)
        connection_3.send(bytes('MESSAGE Jelly Good one', 'utf8'))
        sleep(0.05)
        private_room = self.server.lobbies[2]
        self.assertTrue('Bones: Good one' in private_room.msg_list)
        self.server.close()

    def test_rooms(self):
        connection_5 = socket()
        connection_5.connect((self.host, self.port))
        connection_5.send(bytes('IDENTIFY Bones', 'utf8'))
        sleep(0.005)
        connection_5.send(bytes('CREATEROOM Skelejokes', 'utf8'))
        sleep(0.005)
        found = False
        for room in self.server.lobbies:
            if (room.name == 'Skelejokes'):
                found = True
                r = room
                break

        self.assertTrue(found)
        self.assertEqual(r.owner, 1)
        connection_6 = socket()
        connection_6.connect((self.host, self.port))
        connection_6.send(bytes('IDENTIFY Jelly', 'utf8'))
        sleep(0.005)
        connection_5.send(bytes('INVITE Skelejokes Jelly', 'utf8'))
        sleep(0.005)
        self.assertTrue(2 in r.invited_clients)
        connection_6.send(bytes('JOINROOM Skelejokes', 'utf8'))
        sleep(0.005)
        self.assertTrue(2 in r.accepted_clients)
        connection_5.send(bytes('ROOMESSAGE Skelejokes Bone a petit', 'utf8'))
        sleep(0.005)
        self.assertTrue('Bones: Bone a petit' in r.msg_list)
        connection_6.send(bytes('ROOMESSAGE Skelejokes Stop', 'utf8'))
        sleep(0.005)
        self.assertTrue('Jelly: Stop' in r.msg_list)
        self.server.close()


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)

    unittest.TextTestRunner(verbosity=2, failfast = True).run(suite)
