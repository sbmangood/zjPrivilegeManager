#-*- coding: utf-8 -*-

#import os
import paho.mqtt.client as mqttClient
#import json as json
#import sys
#from pymongo import MongoClient

import queue


# 接受主题发布消息,做出相应的处理
def on_message(client, userdata, msg):

    try:
        client.mesQueue.put(msg.payload)
    except:
        print("unkown err on_message")

def on_connect(self, userdata, flags, rc):
    print("MQTT 连接成功")
    for topic in self.subTopics:
        self.subscribe(topic)


# 定义一个MQTT类
class MyMQTTClient(mqttClient.Client):

    mesQueue=queue.Queue(1)
    subTopics=[]

    def m__init__(self,q=queue.Queue(1)):
        self.mesQueue=q
        self.on_message=on_message
        self.on_connect=on_connect


    # mqtt连接函数
    def connect_mqtt(self, ip, port, heart):

        print("connect mqtt")
        rc=self.connect(ip,port,heart)
        print (rc)

        self.loop_forever()





    def m_sub(self,topic):

        if topic not in self.subTopics:
            self.subTopics.append(topic)

            try:
                self.subscribe(topic)
                #print ("mqtt sub %s topic ok!",topic)
            except:
                print("mqtt sub %s topic err!", topic)


    def m_pub(self,topic,msg):

        try:
            self.publish(topic,msg,1)
        except:
            print("mqtt publish %s topic err!", topic)
