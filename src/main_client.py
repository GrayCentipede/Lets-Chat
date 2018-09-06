import sys
from threading import Thread

from Client import Client


if __name__ == '__main__':
    args = sys.argv
    if (len(args) < 3):
        print('Usage: python main_client.py host port')
        quit()
    name = raw_input('Enter your name: ')
    c = Client(name)
    c.connect(host = args[1], port = int(args[2]))
    send_thread = Thread(target=c.send_msg)
    receive_thread = Thread(target=c.receive_from_server)
    send_thread.daemon = receive_thread.daemon = True
    send_thread.start()
    receive_thread.start()
    while c.is_connected:
        continue
