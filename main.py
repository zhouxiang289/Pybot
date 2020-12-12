import requests
import json 
import asyncio
import websockets
import os
import configparser
import redis

async def getMessage(wsurl:str,sessionkey:str):
    async with websockets.connect(str(wsurl)+"/message?sessionKey="+str(sessionkey)) as websocket:
        message = await websocket.recv()
        message = json.loads(message)
        messagedb.toSet(MessageManager.getMessageId(message),message) #redis存入消息
        MessageManager.announce(messageId,message)
async def getEvent(wsurl:str,sessionKey:str):
    async with websockets.connect(str(wsurl)+"/event?sessionKey="+str(sessionkey)) as websocket:
        event = await websocket.recv()
        event = json.loads(event)
        messagedb.toSet(MessageManager.getMessageId(message),message) #redis存入消息
        EvnetManager.announce(eventId,event)

class RedisManager():
    connection = None
    def __init__(self,host:str,port:int,db:int=1):
        self.connection = redis.StrictRedis(host,port,db,decode_responses=True)
    def toSet(self,key,value,extime=-1):
        self.connection.set(key,value)
        self.connection.expire(key,extime)
    def toGet(self,key):
        return self.connection.get(key)
    def toDel(self,key):
        self.connection.delete(key)
    def isExists(self,key):
        return self.connection.exists(key)
    def keyLenth(self):
        return self.connection.dbsize()

class Request:
    def httpGet(self,url:str):
        r = requests.get(url)
        return json.loads(r.text)
    def httpPost(self,url,postdata:str):
        r = requests.post(url,data = postdata)
        return json.loads(r.text)

class CreateSession(Request):
    sessionKey = None
    def __init__(self,botqq:int,authKey:str):
        self.sessionKey = self.httpPost(url+"/auth",json.dumps({"authKey": authKey}))["session"]
        self.httppost(url+"/verify",json.dumps({"sessionKey":self.sessionkey,"qq":botqq}))
    def getSessionKey():
        return self.sessionKey

class MessageManager:
    def __init__(self,)
    @staticmethod
    def getMessageId(message):
        if "messageId" in message:
            return message["messageId"]
        elif "messageChain" in message:
            return message["messageChain"][0]["id"]
