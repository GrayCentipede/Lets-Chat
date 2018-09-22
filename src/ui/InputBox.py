import npyscreen

"""
An interface for the input box.
To generate HTML documentation for this module use the command:

    pydoc -w src.ui.InputBox

"""

class InputBox(npyscreen.BoxTitle):
    """
    npyscreen's MultiLineEdit now will be surrounded by a box
    """
    
    _contained_widget = npyscreen.MultiLineEdit
