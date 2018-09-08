import npyscreen

from .InputBox import InputBox

class PopUpScreen(npyscreen.ActionForm):
    def create(self):
        # Get the space used by the form
        y, x = self.useable_space()
        self.add(InputBox, name="Enter your username", value = "Example: FlowerBoy",
                    relx=x // 4, max_width = x // 2, max_height = y // 4)
        self.add(InputBox, name="Rules", value = "...", editable = False,
                    relx=x // 4, max_width = x // 2, max_height = y // 4)

    def on_ok(self):
        self.parentApp.setNextForm("CHAT")
    def on_cancel(self):
        self.parentApp.setNextForm(None)
