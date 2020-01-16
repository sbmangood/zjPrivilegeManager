#-*- coding: utf-8 -*-


from mqtt.mqttClass import *
import queue
import threading
import time

from m_casbin.casbinClass import *
from globalData.m_globalData import *

casbinModelFiltPath='./configs/midWare/rbac_model.conf'


def main():




    #读取配置文件
    globalData=M_GlobalData()
    globalData.initData()

    #产生一个消息队列
    q=queue.Queue()
    #给消息队列一个互斥锁
    queueLock=threading.Lock()

    #初始化MQTT类
    mc=MyMQTTClient()
    mc.m__init__(q)

    try:
        fd = open(casbinModelFiltPath, mode='r', encoding='utf-8')
        fd.close()
    except:
        print(casbinModelFiltPath," 配置文件没有读到,程序无法正确执行,请关闭程序,检查原因!")
        while True:
            time.sleep(10)

    #初始cansbin 权限管理类
    mcb=Mcasbin(casbinModelFiltPath,globalData.mongodbUrl)
    mcb.getQueueAndmqttClient(q,mc)
    mcb.setPubReplyTopic(globalData.midWareReplyPubMqttTopic)
    mcb.setPubTransmitTopic(globalData.midWareTranmitPubMqttTopic)


    #mqtt 类的线程
    mqttLoopThread=threading.Thread(target=mc.connect_mqtt,
                                    args=(globalData.mqttIp,
                                          globalData.mqttPort,60))
    mqttLoopThread.start()

    #权限管理类的线程
    mcbThr=threading.Thread(target=mcb.casbinWork,args=())
    mcbThr.start()


    time.sleep(2)
    #开启MQTT类的监听主题
    for item in globalData.midWareSubMqttTopics:
        print(item)
        mc.m_sub(item)



#运行主函数
main()

