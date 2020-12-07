import requests
import json 
import asyncio
import websockets
import os
import configparser

async def getMessage(wsurl,sessionkey:str):
    async with websockets.connect(str(wsurl)+"/message?sessionKey="+str(sessionkey)) as websocket:
        message = await websocket.recv()
        message = json.loads(message)
        #redis接入
        MessageManager.announce(messageId,message)
async def getEvent(wsurl,sessionKey:str):
    async with websockets.connect(str(wsurl)+"/event?sessionKey="+str(sessionkey)) as websocket:
        event = await websocket.recv()
        event = json.loads(event)
        #redis接入
        EvnetManager.announce(eventId,event)

class Request:
    def httpGet(self,url:str):
        r = requests.get(url)
        return json.loads(r.text)
    def httpPost(self,url,postdata:str):
        r = requests.post(url,data = postdata)
        return json.loads(r.text)

class CreateSession(Request):
    sessionKey = None
    def __init__(self,botqq:int,authKey):str:
        self.sessionKey = self.httpPost(url+"/auth",json.dumps({"authKey": authKey}))["session"]
        self.httppost(url+"/verify",json.dumps({"sessionKey":self.sessionkey,"qq":botqq}))
    def getSessionKey():
        return self.sessionKey

class MessageManager:
    def __init__(self,)