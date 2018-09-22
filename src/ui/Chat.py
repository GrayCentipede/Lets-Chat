from time import sleep
import npyscreen
import curses
import socket

from .InputBox import InputBox
from .ListBox import ListBox
from ..ClientStatus import ClientStatus

"""
An interface for the chat.
To generate HTML documentation for this module use the command:

    pydoc -w src.ui.Chat

"""

class Chat(npyscreen.FormBaseNew):
    """
    Chat has all the widgets and functionality so that it can work with any given server (that follows the
    given protocol)
    """

    chat_rooms = None
    username = None

    def create(self):
        """
        Creates the widgets and the room chats where the messages will be stored.
        """

        self.username = str(self.parentApp.client_controller.get_client_name())
        self.chat_rooms = {0: ['PUBLIC', []], 1: [self.username, []]}

        y, x = self.useable_space()
        self.rooms = self.add(npyscreen.BoxTitle, name="Rooms", values = ['PUBLIC', self.username], value = 0,
                                relx= (x//30), rely = (y // 15), max_width = x // 5 )
        self.msg_list = self.add(ListBox, name="Hey, have a look!", footer = 'PUBLIC',
                                relx=(x//4), rely = (y // 15), max_height = (3*y // 5))
        self.status_box = self.add(InputBox, name="Status", value= "...",
                     editable = False, relx=x // 4, rely = (3*y // 4), max_height = y // 15)
        self.msg_box = self.add(InputBox, name="Write something cute",
                                footer = 'User - ' + self.username, color = 'SAFE',
                                relx=x // 4)

        new_handlers = {
            # Set ctrl+Q to exit
            "^Q": self.exit_chat,
            # Set ctrl+R to load chat room
            "^R": self.load_chat_room,
            # Set alt+enter to send a message
            curses.ascii.alt(curses.ascii.NL): self.msg_box_clear
        }

        self.add_handlers(new_handlers)

    def load_chat_room(self, _input):
        """
        When an event is triggered it loads all the messages from a room into the msg list box.

        :param _input: The input that triggered the event
        """

        msgs = self.chat_rooms[self.rooms.value][1]
        self.msg_list.values = msgs
        self.msg_list.footer = self.chat_rooms[self.rooms.value][0]
        self.msg_list.display()


    def exit_chat(self, _input = None):
        """
        When an event (or not) is triggered it exits the chat, ending the connection and closing the app.

        :param _input: The input that triggered the event
        """

        try:
            self.parentApp.client_controller.disconnect_client()
            sleep(0.05)
            exit(0)
        except socket.error as err:
            self.status_box.value = str(err)

    def update_status(self):
        """
        Updates the app depending on the client's status
        """

        status = self.parentApp.client_controller.get_client_status()
        if (status == ClientStatus.ACTIVE):
            self.msg_box.color = self.rooms.color = self.msg_list.colour = self.status_box.colour = 'SAFE'
        elif (status == ClientStatus.AWAY):
            self.msg_box.color = self.rooms.color = self.msg_list.colour = self.status_box.colour = 'DANGER'
        else:
            self.msg_box.color = self.rooms.color = self.msg_list.colour = self.status_box.colour = 'CAUTION'

        self.status_box.display()
        self.rooms.display()
        self.msg_list.display()

    def msg_box_clear(self, _input):
        """
        When an event is triggered it send the message that was in the input box.

        :param _input: The input that triggered the event
        """

        try:
            self.username = str(self.parentApp.client_controller.get_client_name())
            content = self.msg_box.value
            self.parentApp.client_controller.send_msg(content)
            self.msg_box.value = ''
            self.msg_box.footer = 'User - ' + self.username
            self.update_status()

            if ('IDENTIFY' in content):
                chunks = content.split()
                new_name = chunks[1]
                self.chat_rooms[1][0] = new_name
                self.rooms.values[1] = new_name
                self.rooms.display()

            if ('DISCONNECT' in content):
                sleep(0.5)
                self.exit_chat()
                return

        except socket.error as err:
            self.status_box.value = str(err)
            self.status_box.display()

        self.msg_box.display()

    def create_new_chat_room(self, id, name):
        """
        Creates a new room chat and appends it to the list of rooms available on the chat.

        :param id: The id of the new room
        :param name: The room's name
        """

        self.chat_rooms[id] = [name, []]
        self.rooms.values.append(name)


    def get_chat_room(self, msg):
        """
        Gets the respective room so that the message can be appended and displayed

        :param msg: The message
        :return: room id, room's message list
        """

        chunks = msg.split()
        # If it's a public message
        if ('...PUBLIC' in msg and '...INVALID' not in msg) or (chunks[0].count(':') == 0 and '...' not in chunks[0]):
            return 0, self.chat_rooms[0][1]
        # If it's a private message from the server or the author himself
        elif ('...' in msg and ' ... ' not in msg and '... ' not in msg and msg.count('-') == 0 or '...INVALID' in msg):
            return 1, self.chat_rooms[1][1]
        else:
            # If it's an user
            if (chunks[0].count(':') == 1 and '...' not in chunks[0]):
                username = chunks[0].replace(':', '')
                id_count = 0

                for room_id in self.chat_rooms:
                    id_count = room_id
                    room_name = self.chat_rooms[room_id][0]
                    if (room_name == username):
                        return room_id, self.chat_rooms[room_id][1]

                self.create_new_chat_room(id_count + 1, username)
                return id_count + 1, self.chat_rooms[id_count + 1][1]

            # It's a room message
            else:
                response = chunks[0].split('-')
                room_name_a = response[0].replace('...', '')

                id_count = 0

                for room_id in self.chat_rooms:
                    id_count = room_id
                    room_name_b = self.chat_rooms[room_id][0]
                    if (room_name_a == room_name_b):
                        return room_id, self.chat_rooms[room_id][1]

                self.create_new_chat_room(id_count + 1, room_name_a)
                return id_count + 1, self.chat_rooms[id_count + 1][1]


    def append_msg_to_room(self, msg, room_msg_list):
        """
        Appends a message to a room's message list

        :param msg: The message
        :param room_msg_list: The room's message list
        """

        # limit of characters in a single line in the msg list
        n = 119
        msg_content = msg.split('\n')
        for content in msg_content:
            if (len(content) > 119):
                sub_contents = [msg[i:i+n] for i in range(0, len(content), n)]
                for sub_content in sub_contents:
                    room_msg_list.append(sub_content)
            else:
                room_msg_list.append(content)

    def append_msg(self, msg):
        """
        Appends and displays a received message where it is supposed to be.

        :param msg: The message
        """
        
        try:
            room_id, room_msg_list = self.get_chat_room(msg)

            self.append_msg_to_room(msg, room_msg_list)

            self.msg_list.values = room_msg_list
            self.rooms.value = room_id
            self.msg_list.footer = self.rooms.values[room_id]
        except Exception as e:
            self.status_box.value = str(e)
            self.status_box.display()

        self.msg_list.display()
        self.rooms.display()
