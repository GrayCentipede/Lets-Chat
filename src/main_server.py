from threading import Thread

import sys

from Server import Server

if __name__ == '__main__':
    args = sys.argv
    if (len(args) < 4):
        print('Usage: python Server.py host port number_of_conections')
        quit()
    server = Server(host = args[1], port = int(args[2]), num_conections = int(args[3]))
    Thread(target=server.accept_conections).start()
