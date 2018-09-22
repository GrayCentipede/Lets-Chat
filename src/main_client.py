import sys
from threading import Thread

from .Client import Client
from .ui.ChatApp import App


if __name__ == '__main__':
    args = sys.argv
    if (len(args) == 2):
        print('Usage: python main_client.py')
        quit()

    app = App()
    app.run()
