#-*- coding: utf-8 -*-

import json
import os

globalDataConfigFilePath="./configs/midWare/globalData.json"

def isJson(str):
    try:
        js=json.loads(str)

    except ValueError:


        return False

    return True


def getJsonData(js,key):

    if (js.get(key)):
        return js[key]
    else:
        return None



class M_GlobalData(object):

    fileJs="{}"

    mqttIp="127.0.0.1"
    mqttPort=1883


    midWareSubMqttTopics=["wwwToPMMidware"]
    midWareReplyPubMqttTopic="wwwWebSocketMqttTopic"
    midWareTranmitPubMqttTopic="AUTO_TOPIC"


    mongodbUrl='mongodb://127.0.0.1:27017/'



    def initData(self):

        str=""
        try:
            fd=open(globalDataConfigFilePath,mode='r+',encoding='utf-8')
            str=fd.read()
            fd.close()
        except:
            print(globalDataConfigFilePath ," 配置文件读取错误,采用默认初始化参数!")
            return

        if isJson(str):
            self.fileJs=json.loads(str)

        if (self.fileJs=="{}"):
            print("json file err")
            return

        self.mqttIp=getJsonData(self.fileJs,"mqttIp")
        self.mqttPort=getJsonData(self.fileJs,"mqttPort")


        if self.fileJs.get("midWareSubMqttTopics"):
            mwsmtJs=self.fileJs["midWareSubMqttTopics"]
            self.midWareSubMqttTopics=[]
            for item in mwsmtJs:
                self.midWareSubMqttTopics.append(item)


        self.midWareReplyPubMqttTopic=getJsonData(self.fileJs,"midWareReplyPubMqttTopic")
        self.midWareTranmitPubMqttTopic=getJsonData(self.fileJs,"midWareTranmitPubMqttTopic")

        self.mongodbUrl = getJsonData(self.fileJs, "mongodbUrl")

        #print(self.mongodbUrl)

        print("Get global data ok!")