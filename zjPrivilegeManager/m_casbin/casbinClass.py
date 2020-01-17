#-*- coding: utf-8 -*-

import  sys
#from m_casbin.mJsonAdapter.mJsonAdapter import *
import queue
import  string

import time
from mqtt.mqttClass import *

from m_casbin.mMongoAdapter.mMongoAdapter import *

from login.loginManager import *



NOT_JSON=-1
PRIVILEGE_OK=0
PRIVILEGE_ERR=1
PRIVILEGE_NOT_LOGIN="notLogin"

#MQTT_PUB_TRANSMIT_TOPIC="AUTO_TOPIC"
#MQTT_PUB_REPLY_TOPIC="wwwWebSocketMqttTopic"


replyPermissionOk={"permission":"ok"}
replyPermissionErr={"permission":"err"}
replyPermissionNotLogin={"permission":"notLogin"}

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

    loginManager=LoginManager();

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

    def loginDeal(self,msg,heartReply="false"):

        ret=self.loginManager.jsMessageDeal(msg)
        #print(ret)

        if(ret==LOGIN_TYPE_ERR):
            return ret

        type=""
        type=getJsStr(msg,LOGIN_TYPE)


        if(heartReply!="true" and type==LOGIN_TYPE_HEART):
            return ret

        sendJs={}

        sendJs[LOGIN_TYPE]=ret
        self.mqttClient.m_pub(self.mqttPubReplyTopic, str(sendJs))

        return ret

    def casbinWork(self):
        print("casbinWork start")

        while True:
            if not self.m_queue.empty():
                msg=self.m_queue.get()
                msg = msg.decode('utf-8')
                if not isJson(msg):
                    print("not json")
                    continue
                js = json.loads(str(msg))
                #result=self.loginManager.jsMessageDeal(msg)

                if(self.loginDeal(js)!=LOGIN_TYPE_ERR):
                    continue
                #msg=self.m_queue.pop()
                ret=self.judgePrivlege(js)

                if(ret==PRIVILEGE_OK):# PRIVILEGE_OK
                    #print("permission ok")
                    self.mqttClient.m_pub(self.mqttPubReplyTopic,str(replyPermissionOk))
                    self.mqttClient.m_pub(self.mqttPubTransmitTopic,msg)
                elif(ret==PRIVILEGE_ERR):
                    #print(self.mqttPubReplyTopic)
                    self.mqttClient.m_pub(self.mqttPubReplyTopic, str(replyPermissionErr))
                    #print("permission err")
                elif(ret==PRIVILEGE_NOT_LOGIN):
                    self.mqttClient.m_pub(self.mqttPubReplyTopic, str(replyPermissionNotLogin))

            time.sleep(0.1)

    def judgePrivlege(self,js):

        #msg=msg1.encode('utf-8').decode('utf-8')
        #msg=msg.replace("\\n","").strip()


        #print(msg)
        #if not isJson(str(msg)):
        #    return NOT_JSON
        #js=json.loads(str(msg))
        name=getJsStr(js,"userName")

        self.loginManager.usrListMutex.acquire()
        if(not self.loginManager.usrList.get(name)):
            self.loginManager.usrListMutex.release()
            return PRIVILEGE_NOT_LOGIN
        self.loginManager.usrListMutex.release()


        resource=getJsStr(js,"resource")
        privilege=getJsStr(js,"operate")

        if (self.enforcer.enforce(name,resource,privilege)):
            replyPermissionOk["userName"]=name
            return PRIVILEGE_OK
        else:
            replyPermissionErr["userName"] = name
            return PRIVILEGE_ERR










