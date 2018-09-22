from threading import Thread

import sys
import signal

from .Server import Server

def usage():
    print('Usage: python3 -m src.main_server [-b host] port number_of_conections [-d]')
    quit()

if __name__ == '__main__':
    type = 'normal'
    host = '0.0.0.0'
    port = 0
    args = sys.argv
    num_con = 0

    try:
        if ('-help' in args):
            usage()

        if ('-d' in args):
            type = 'debug'
        if ('-b' in args):
            i = args.index('-b')
            host = args[i + 1]
            port = args[i + 2]
            num_con = args[i + 3]
        else:
            port = args[1]
            num_con = args[2]

        if (3 <= len(args) <= 6):
            server = Server(host = host, port = int(port), num_conections = int(num_con), mode = type)
            server.accept_conections()
        else:
            usage()
    except:
        usage()
