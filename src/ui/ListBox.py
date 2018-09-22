import npyscreen

"""
An interface for the list box.
To generate HTML documentation for this module use the command:

    pydoc -w src.ui.InputBox

"""

class ListBox(npyscreen.BoxTitle):
    """
    npyscreen's Pager now will be surrounded by a box
    """
    
    _contained_widget = npyscreen.Pager
