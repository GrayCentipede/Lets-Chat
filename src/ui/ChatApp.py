import npyscreen

from .PopUpScreen import PopUpScreen
from .Chat import Chat
from ..ClientController import ClientController

"""
The app for the chat
To generate HTML documentation for this module use the command:

    pydoc -w src.ui.ChatApp

"""

class App(npyscreen.StandardApp):
    """
    App contains the forms of the SIGN IN and the chat itself. It also has a client's controller.
    """

    client_controller = None

    def onStart(self):
        """
        Intializes the app
        """

        self.client_controller = ClientController(self)
        self.sign_room = self.addForm("MAIN", PopUpScreen, name="Sign in")
        self.chat_room = self.addForm("CHAT", Chat, name="Let's Chat v0.0")
