import npyscreen
import socket

from .InputBox import InputBox
from .ListBox import ListBox

"""
An interface for the sign in screen.
To generate HTML documentation for this module use the command:

    pydoc -w src.ui.PopUpScreen

"""

class PopUpScreen(npyscreen.ActionForm):
    """
    PopUpScreen is an interface so that the client can connect to a server given the host and port.
    """

    def create(self):
        """
        Instance the neccesary widgets for the form to work
        """

        rules = []
        rules.append('Send a message with: alt+enter.')
        rules.append('Show messages from a room with: ctrl+R.')
        rules.append('Exit with: ctrl+Q.')
        rules.append('Enter a message in the exact format of the given protocol.')
        rules.append('Enjoy and be gentle with the system.')
        rules.append('')
        rules.append('cancel - exit app')
        rules.append('ok - try to connect')

        y, x = self.useable_space()
        self.host_box = self.add(InputBox, name="Enter the host:",
                    relx=x // 4, max_width = x // 2, max_height = y // 15)
        self.port_box = self.add(InputBox, name="Enter the port",
                    relx=x // 4, max_width = x // 2, max_height = y // 15)
        self.rules_box = self.add(ListBox, name="Rules", values = rules, editable = False,
                    relx=x // 4, max_width = x // 2, max_height = y // 4)
        self.status_box = self.add(InputBox, name="Status", value= "You have not connected.",
                     editable = False, relx=x // 4, max_width = x // 2, max_height = y // 15)

    def on_ok(self):
        """
        Function to be executed when the users clicks on the button ok
        It sets the next form if and only if the client could connect to the server.
        """

        host = self.host_box.value
        port = self.port_box.value
        try:
            port = int(port)
            self.parentApp.client_controller.connect_client(host, port)
            self.parentApp.client_controller.set_client_listener()
            self.parentApp.setNextForm('CHAT')
        except ValueError:
            self.status_box.value = 'Port must be an integer'
        except socket.error as exc:
            self.status_box.value = 'Invalid host or port ||| ' + str(exc)

    def on_cancel(self):
        """
        Function to be executed when the users clicks on the button ok
        Exists the app.
        """

        self.parentApp.setNextForm(None)
