class Plugin:
    def onLoad(self):
        print("hello")


class MessageRecv:
    def onMessage(self,messageid,message,type):
        print("yes")


def getPluginClass():
    return Plugin


def getMessageRecvClass():
    return MessageRecv
