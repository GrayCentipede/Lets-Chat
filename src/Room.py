class Room(object):

    name = None
    msg_list = []

    def __init__(self, name):
        self.name = name

    def add_msg(self, msg):
        self.msg_list.append(msg)
