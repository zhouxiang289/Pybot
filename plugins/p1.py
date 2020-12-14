from plugins.__interface import *


class Plugin(PluginBase):
    def __init__(self):
        super(Plugin, self).__init__()

    def onLoad(self):
        print("hello")

    def onDisable(self):
        pass


class MessageRecv:
    def onMessage(self, messageid, message):
        print("yes")

    def onEvent(self):
        pass


def getPluginClass():
    return Plugin


def getMessageRecvClass():
    return MessageRecv
