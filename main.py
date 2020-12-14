import requests
import json
import asyncio
import websockets
import os
import redis
import sys

# pluginloaded = []
# pluginobj = []
pluginloaded = {}


async def getMessage(wsurl: str, sessionkey: str):
    async with websockets.connect(str(wsurl) + "/message?sessionKey=" + str(sessionkey)) as websocket:
        logger.info("开始监听消息")
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            logger.info("接收到新的消息包:" + str(message))
            # messagedb.toSet(MessageManager.getMessageId(message), message)  # redis存入消息
            MessageManager.announce(MessageManager.getMessageId(message), message)


async def getEvent(wsurl: str, sessionkey: str):
    async with websockets.connect(str(wsurl) + "/event?sessionKey=" + str(sessionkey)) as websocket:
        logger.info("开始监听事件")
        while True:
            event = await websocket.recv()
            event = json.loads(event)
            logger.info("接收到新的事件包:" + str(event))
            # messagedb.toSet(MessageManager.getMessageId(event), event)  # redis存入消息
            EventManager.announce(EventManager.getMessageId(event), event)


class logger:
    @staticmethod
    def info(log):
        print("[INFO]" + str(log))

    @staticmethod
    def warn(log):
        print("[WARN]" + str(log))


class RedisManager:
    connection = None

    def __init__(self, host: str, port: int, db: int = 1):
        self.connection = redis.StrictRedis(host, port, db, decode_responses=True)

    def toSet(self, key, value, extime=-1):
        self.connection.set(key, value)
        self.connection.expire(key, extime)

    def toGet(self, key):
        return self.connection.get(key)

    def toDel(self, key):
        self.connection.delete(key)

    def isExists(self, key):
        return self.connection.exists(key)

    def keyLenth(self):
        return self.connection.dbsize()


class Request:
    @staticmethod
    def httpGet(url: str):
        r = requests.get(url)
        return json.loads(r.text)

    @staticmethod
    def httpPost(url, postdata: str):
        r = requests.post(url, data=postdata)
        return json.loads(r.text)


class CreateSession:
    sessionKey = None

    def __init__(self, botqq: int, authKey: str, url: str):
        self.sessionKey = Request.httpPost(url=url + "/auth", postdata=json.dumps({"authKey": authKey}))["session"]
        logger.info("获取到sessionkey:" + self.sessionKey)
        Request.httpPost(url + "/verify", json.dumps({"sessionKey": self.sessionKey, "qq": botqq}))
        logger.info("验证sessionkey成功")

    def getSessionKey(self):
        return self.sessionKey


class MessageManager:
    @staticmethod
    def getMessageId(message):
        if "messageId" in message:
            return message["messageId"]
        elif "messageChain" in message:
            return message["messageChain"][0]["id"]

    @staticmethod
    def announce(messageid, message, types):
        for p in list(pluginloaded.keys()):
            p_mod = pluginloaded[p]
            p_class = p_mod.getMessageRecvClass()
            p_obj = p_class()
            p_obj.onMessage(messageid, message)


class EventManager(MessageManager):
    @staticmethod
    def getMessageId(message):
        if "messageId" in message:
            return message["messageId"]
        elif "messageChain" in message:
            return message["messageChain"][0]["id"]

    @staticmethod
    def announce(messageid, message, types):
        for p in list(pluginloaded.keys()):
            p_mod = pluginloaded[p]
            p_class = p_mod.getMessageRecvClass()
            p_obj = p_class()
            p_obj.onEvent(messageid, message)


class PluginManager:
    pluginslist = []

    def __init__(self):
        logger.info("当前工作目录:" + os.getcwd())
        for filename in os.listdir(os.getcwd() + "\\plugins"):
            if filename.endswith(".py") and not filename.startswith("_"):
                logger.info(filename)
                self.pluginslist.append("plugins." + os.path.splitext(filename)[0])
                logger.info(self.pluginslist)
        Module_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nowdir = os.getcwd()
        sptdir = os.path.split(nowdir)
        dirlst = list(sptdir)
        dirlst.pop()
        workdir = "\\".join(dirlst)
        sys.path.append(Module_Dir)
        sys.path.append(workdir)

    def loadAllPlugin(self):
        logger.info("开始加载所有插件")
        for p in self.pluginslist:
            p_mod = __import__(p, fromlist=[p])
            p_class = p_mod.getPluginClass()
            p_obj = p_class()
            p_obj.onLoad()
            pluginloaded[p] = p_mod
            # 这里应该有错误处理
        logger.info("所有插件载入完成")

    def disableAllPlugin(self):
        for p in list(pluginloaded.keys()):
            p_mod = pluginloaded[p]
            p_class = p_mod.getPluginClass()
            p_obj = p_class()
            p_obj.onDisable()
            pluginloaded.pop(p)
        self.pluginloaded.clear()

    def __loadPlugin(self, pluginname):
        if pluginname not in self.pluginloaded:
            p_obj = __import__(pluginname)
            logger.info("正在载入插件" + pluginname)
            p_obj.onLoad()
            logger.info("已载入插件" + pluginname)
            pluginloaded.append(pluginname)
        else:
            pass  # 这里应当引发一个警告

    def __disablePlugin(self, pluginname):
        if pluginname in self.pluginloaded:
            logger.info("正在禁用插件", pluginname)
            p_obj = pluginname.Plugin()
            p_obj.onDisable()
            logger.info("已禁用插件", pluginname)
            pluginloaded.remove(pluginname)
        else:
            pass  # 这里应当引发一个警告


def main():
    wsurl = "ws://zhouxiang289.f3322.net:8080"
    botqq = 2593267832
    authkey = "6397684399qq"
    try:
        pluginbase = PluginManager()
    except Exception as e:
        print(e)
        input()
    pluginbase.loadAllPlugin()
    bot = CreateSession(botqq, authkey, "http://zhouxiang289.f3322.net:8080")
    sessionkey = bot.getSessionKey()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(getEvent(wsurl, sessionkey), getMessage(wsurl, sessionkey)))
    loop.close()


main()
