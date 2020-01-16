#-*- coding: utf-8 -*-

import  sys
#from m_casbin.mJsonAdapter.mJsonAdapter import *
import queue
import  string

import time
from mqtt.mqttClass import *

from m_casbin.mMongoAdapter.mMongoAdapter import *

NOT_JSON=-1
PRIVILEGE_OK=0
PRIVILEGE_ERR=1

#MQTT_PUB_TRANSMIT_TOPIC="AUTO_TOPIC"
#MQTT_PUB_REPLY_TOPIC="wwwWebSocketMqttTopic"


replyPermissionOk={"permission":"ok"}
replyPermissionErr={"permission":"err"}
#replyPermissionNotJson={"permission":"notJson"}


def isJson(str):
    try:
        js=json.loads(str)

    except ValueError:


        return False

    return True

def getJsStr(js=json.loads("{}"),key="none"):
    if key in js:
        return js[key]
    else:
        return "none"


class Mcasbin(object):
    enforcer=None
    m_queue=queue.Queue(1)
    mqttClient=MyMQTTClient()
    mongoUrl='mongodb://127.0.0.1:27017/'

    mqttPubReplyTopic="wwwWebSocketMqttTopic"
    mqttPubTransmitTopic="AUTO_TOPIC"

    #mqttSubTopics=[""]


    def __init__(self,modelFile,policeFile):
        #adapter=jsonAdapter(policeFile)
        self.mongoUrl=policeFile
        adapter=MongoAdapter(self.mongoUrl)
        adapter.connectDb()
        self.enforcer=casbin.Enforcer(modelFile,adapter,True)

    def getQueueAndmqttClient(self,q,mqttC):
        self.m_queue=q
        self.mqttClient=mqttC
    def setPubReplyTopic(self,str):
        self.mqttPubReplyTopic=str
    def setPubTransmitTopic(self,str):
        self.mqttPubTransmitTopic=str

    def casbinWork(self):
        print("casbinWork start")

        while True:
            if not self.m_queue.empty():
                msg=self.m_queue.get()
                #msg=self.m_queue.pop()
                ret=self.judgePrivlege(msg)

                if(ret==NOT_JSON):
                    print ("not json")
                    #pass
                elif(ret==PRIVILEGE_OK):# PRIVILEGE_OK
                    #print("permission ok")
                    self.mqttClient.m_pub(self.mqttPubReplyTopic,str(replyPermissionOk))
                    self.mqttClient.m_pub(self.mqttPubTransmitTopic,msg)
                else:
                    #print(self.mqttPubReplyTopic)
                    self.mqttClient.m_pub(self.mqttPubReplyTopic, str(replyPermissionErr))
                    #print("permission err")
            time.sleep(0.1)

    def judgePrivlege(self,msg):

        #msg=msg1.encode('utf-8').decode('utf-8')
        #msg=msg.replace("\\n","").strip()

        msg=msg.decode('utf-8')
        #print(msg)
        if not isJson(str(msg)):
            return NOT_JSON
        js=json.loads(str(msg))
        name=getJsStr(js,"useName")
        resource=getJsStr(js,"resource")
        privilege=getJsStr(js,"operate")

        if (self.enforcer.enforce(name,resource,privilege)):
            replyPermissionOk["useName"]=name
            return PRIVILEGE_OK
        else:
            replyPermissionErr["useName"] = name
            return PRIVILEGE_ERR










