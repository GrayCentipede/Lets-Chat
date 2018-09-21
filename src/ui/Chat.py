from time import sleep
import npyscreen
import curses
import socket

from .InputBox import InputBox
from .ListBox import ListBox

class Chat(npyscreen.FormBaseNew):

    def create(self):
        y, x = self.useable_space()
        self.rooms = self.add(npyscreen.BoxTitle, name="Rooms", values = ['PUBLIC'], value = 0,
                                relx= (x//30), rely = (y // 15), max_width = x // 5 )
        self.msg_list = self.add(ListBox, name="Hey, have a look!", footer = 'PUBLIC',
                                relx=(x//4), rely = (y // 15), max_height = (3*y // 5))
        self.status_box = self.add(InputBox, name="Status", value= "...",
                     editable = False, relx=x // 4, rely = (3*y // 4), max_height = y // 15)
        self.msg_box = self.add(InputBox, name="Write something cute",
                                footer = 'User - ' + str(self.parentApp.client_controller.get_client_name()),
                                relx=x // 4)

        new_handlers = {
            # Set ctrl+Q to exit
            "^Q": self.exit_chat,
            # Set alt+enter to clear boxes
            curses.ascii.alt(curses.ascii.NL): self.msg_box_clear
        }

        self.add_handlers(new_handlers)

    def exit_chat(self, _input):
        try:
            self.parentApp.client_controller.disconnect_client()
            sleep(0.05)
            exit(0)
        except socket.error as err:
            self.status_box.value = str(err)

    def msg_box_clear(self, _input):
        try:
            content = self.msg_box.value
            self.parentApp.client_controller.send_msg(content)
            self.msg_box.value = ''
            self.msg_box.footer = 'User - ' + str(self.parentApp.client_controller.get_client_name())
        except socket.error as err:
            self.status_box.value = str(err)

        self.msg_box.display()

    def append_msg(self, msg):
        msg_content = msg.split('\n')
        for content in msg_content:
            self.msg_list.values.append(content)
        self.msg_list.display()
