import npyscreen

from .PopUpScreen import PopUpScreen
from .Chat import Chat
from ..ClientController import ClientController

class App(npyscreen.StandardApp):

    client_controller = None

    def onStart(self):
        self.client_controller = ClientController(self)
        self.sign_room = self.addForm("MAIN", PopUpScreen, name="Sign in")
        self.chat_room = self.addForm("CHAT", Chat, name="Let's Chat v0.0")

LetsChat = App()
LetsChat.run()
