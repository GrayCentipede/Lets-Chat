import npyscreen

from .PopUpScreen import PopUpScreen
from .Chat import Chat

class App(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", PopUpScreen, name="Sign in")
        self.addForm("CHAT", Chat, name="Let's Chat v0.0")

LetsChat = App()
LetsChat.run()
