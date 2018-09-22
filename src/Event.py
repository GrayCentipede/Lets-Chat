from enum import Enum

"""
An enumeration for the different events we can have.
To generate HTML documentation for this module use the command:

    pydoc -w src.Event

"""

class Event(Enum):
    """
    Event is an enumeration for the different events we can have.
    """

    IDENTIFY = 0
    USERS = 1
    MESSAGE = 2
    PUBLICMESSAGE = 3
    CREATEROOM = 4
    INVITE = 5
    JOINROOM = 6
    ROOMESSAGE = 7
    DISCONNECT = 8
    STATUS = 9
    INVALID = -1

    @classmethod
    def get_event(cls, msg):
        """
        Return the event that the message specified.

        :param msg: The message
        :return: The event it corresponds to.
        """

        instructions = msg.split()
        event = instructions[0]

        if (event == 'IDENTIFY'):
            return cls.IDENTIFY

        elif (event == 'USERS'):
            return cls.USERS

        elif (event == 'STATUS'):
            return cls.STATUS

        elif (event == 'MESSAGE'):
            return cls.MESSAGE

        elif (event == 'PUBLICMESSAGE'):
            return cls.PUBLICMESSAGE

        elif (event == 'CREATEROOM'):
            return cls.CREATEROOM

        elif (event == 'INVITE'):
            return cls.INVITE

        elif (event == 'JOINROOM'):
            return cls.JOINROOM

        elif (event == 'ROOMESSAGE'):
            return cls.ROOMESSAGE

        elif (event == 'DISCONNECT'):
            return cls.DISCONNECT

        else:
            return cls.INVALID
