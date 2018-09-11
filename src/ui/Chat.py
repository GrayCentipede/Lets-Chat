import npyscreen

from .InputBox import InputBox
from .ListBox import ListBox

class Chat(npyscreen.ActionForm):

    def create(self):
        y, x = self.useable_space()
        self.rooms = self.add(npyscreen.BoxTitle, name="Rooms", values = [x for x in range(100)],
                                relx= (x//30), rely = (y // 15), max_width = x // 5 )
        self.msg_list = self.add(ListBox, name="Hey, have a look!", footer = 'User - Turquoise',
                                values = [x for x in range(1000)],
                                relx=(x//4), rely = (y // 15), max_height = (3*y // 5))
        self.msg_box = self.add(InputBox, name="Write something cute", footer = 'User - FlowerBoy',
                                relx=x // 4, rely = (3*y // 4))

    def on_ok(self):
        self.msg_box.value = ""
    def on_cancel(self):
        self.parentApp.setNextForm(None)
