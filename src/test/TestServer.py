import unittest
from socket import socket, timeout
from threading import Thread
from time import sleep
import random
from ..Server import Server

"""
Unit test to check whether or not the server can handle connections.
To generate HTML documentation for this module use the command:

    pydoc -w src.test.TestServer

"""

class TestServer(unittest.TestCase):
    """
    TestServer contains all the unit tests for the server.
    """

    def setUp(self):
        """
        Creates a new server for every unit test.
        """

        self.host = 'localhost'
        self.port = 30000 + random.randint(0, 20000)
        self.server = Server(host = self.host, port = self.port, mode = 'unittest')
        self.server_thread = Thread(target = self.server.accept_conections, daemon = True)
        self.server_thread.start()
        TestServer.set_up_done = True

    def test_accept_connection_and_disconnect(self):
        """
        Tests if the server accepts connections and responds accordingly in case of disconnection.
        """

        connection_1 = socket()
        connection_1.connect((self.host, self.port))
        connection_1.send(bytes('IDENTIFY Marco', 'utf8'))
        sleep(0.005)
        client_list = self.server.clients
        conn = client_list[0]
        self.assertEqual(conn.name, 'Marco')
        connection_1.send(bytes('DISCONNECT', 'utf8'))
        sleep(0.005)
        self.assertEqual(len(client_list), 0)
        self.server.close()
        sleep(0.005)

    def test_public_msg(self):
        """
        Tests if a conection can send a public message, and that everyone on the server receives it.
        """

        connection_2 = socket()
        connection_2.connect((self.host, self.port))
        connection_2.send(bytes('IDENTIFY Polo', 'utf8'))
        sleep(0.05)
        connection_2.send(bytes('PUBLICMESSAGE Hello everyone', 'utf8'))
        sleep(0.05)
        rooms = self.server.lobbies
        global_room = rooms[0]
        self.assertTrue('Polo: Hello everyone' in global_room.msg_list)
        connection_2.send(bytes('DISCONNECT', 'utf8'))
        sleep(0.05)
        self.server.close()

    def test_private_msg(self):
        """
        Tests if a connection can send a private message to another connection.
        """

        connection_3 = socket()
        connection_4 = socket()
        connection_3.connect((self.host, self.port))
        connection_4.connect((self.host, self.port))
        connection_3.send(bytes('IDENTIFY Bones', 'utf8'))
        connection_4.send(bytes('IDENTIFY Jelly', 'utf8'))
        sleep(0.05)
        connection_4.send(bytes('MESSAGE Bones TromBONE', 'utf8'))
        sleep(0.05)
        private_room = self.server.lobbies[2]
        self.assertTrue('Jelly: TromBONE' in private_room.msg_list)
        connection_3.send(bytes('MESSAGE Jelly Good one', 'utf8'))
        sleep(0.05)
        private_room = self.server.lobbies[2]
        self.assertTrue('Bones: Good one' in private_room.msg_list)
        self.server.close()

    def test_rooms(self):
        """
        Tests if the connection can create a room, invite others to it and talk to them through the room.
        """
        
        connection_5 = socket()
        connection_5.connect((self.host, self.port))
        connection_5.send(bytes('IDENTIFY Bones', 'utf8'))
        sleep(0.05)
        connection_5.send(bytes('CREATEROOM Skelejokes', 'utf8'))
        sleep(0.05)
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
        sleep(0.05)
        connection_5.send(bytes('INVITE Skelejokes Jelly', 'utf8'))
        sleep(0.05)
        self.assertTrue(2 in r.invited_clients)
        connection_6.send(bytes('JOINROOM Skelejokes', 'utf8'))
        sleep(0.05)
        self.assertTrue(2 in r.accepted_clients)
        connection_5.send(bytes('ROOMESSAGE Skelejokes Bone a petit', 'utf8'))
        sleep(0.05)
        self.assertTrue('Bones: Bone a petit' in r.msg_list)
        connection_6.send(bytes('ROOMESSAGE Skelejokes Stop', 'utf8'))
        sleep(0.05)
        self.assertTrue('Jelly: Stop' in r.msg_list)
        self.server.close()


if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)

    unittest.TextTestRunner(verbosity=2, failfast = True).run(suite)
