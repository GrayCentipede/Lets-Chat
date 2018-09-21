import npyscreen
import socket

from .InputBox import InputBox

class PopUpScreen(npyscreen.ActionForm):
    def create(self):
        # Get the space used by the form
        y, x = self.useable_space()
        self.host_box = self.add(InputBox, name="Enter the host:",
                    relx=x // 4, max_width = x // 2, max_height = y // 15)
        self.port_box = self.add(InputBox, name="Enter the port",
                    relx=x // 4, max_width = x // 2, max_height = y // 15)
        self.rules_box = self.add(InputBox, name="Rules", value = "...", editable = False,
                    relx=x // 4, max_width = x // 2, max_height = y // 4)
        self.status_box = self.add(InputBox, name="Status", value= "You have not connected.",
                     editable = False, relx=x // 4, max_width = x // 2, max_height = y // 15)

    def on_ok(self):
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
        self.parentApp.setNextForm(None)
