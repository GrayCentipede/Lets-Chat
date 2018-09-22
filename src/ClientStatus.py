from enum import Enum

"""
An enumeration for the different status a client can have.
To generate HTML documentation for this module use the command:

    pydoc -w src.ClientStatus

"""

class ClientStatus(Enum):
    """
    ClientStatus is an enumeration for the different status a client can have.
    """

    ACTIVE = 2
    BUSY = 1
    AWAY = 0
