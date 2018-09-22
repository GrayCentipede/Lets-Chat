from threading import Thread

import sys
import signal

from .Server import Server

def usage():
    print('Usage: python Server.py port number_of_conections [-d]')
    print('       python Server.py port number_of_conections')
    print('       python Server.py host port number_of_conections -b [-d]')
    quit()

if __name__ == '__main__':
    type = 'normal'
    host = '0.0.0.0'
    port = 0
    args = sys.argv
    num_con = 0

    if ('-help' in args):
        usage()

    if ('-d' in args):
        type = 'debug'
    if ('-b' in args):
        host = args[1]
        port = args[2]
        num_con = args[3]
    else:
        port = args[1]
        num_con = args[2]

    if (3 <= len(args) <= 6):
        server = Server(host = host, port = int(port), num_conections = int(num_con), mode = type)
        server.accept_conections()
    else:
        usage()
