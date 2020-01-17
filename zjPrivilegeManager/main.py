#-*- coding: utf-8 -*-


from mqtt.mqttClass import *
import queue
import threading
import time

from m_casbin.casbinClass import *
from globalData.m_globalData import *
from login.loginManager import *

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

    #生成一个登录管理器
    lgm=LoginManager(globalData.mongodbUrl,60,5,2)
    lgm.connectDb()




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
    mcb.loginManager=lgm                    #给权限管理器一个登录器


    #mqtt 类的线程
    mqttLoopThread=threading.Thread(target=mc.connect_mqtt,
                                    args=(globalData.mqttIp,
                                          globalData.mqttPort,60))
    mqttLoopThread.start()

    #权限管理类的线程
    mcbThr=threading.Thread(target=mcb.casbinWork,args=())
    mcbThr.start()

    #登录器的线程,主要是更新心跳数,心跳数定时递减
    lgmThr=threading.Thread(target=lgm.run,args=())
    lgmThr.start()

    #print(lgm.registerNewUsr("仰望", "zhijintech", "QQ:2433022001"))
    print(lgm.loginNewUsr(""
                          ""
                          ""
                          "", "zhijintech"))

    time.sleep(2)
    #开启MQTT类的监听主题
    for item in globalData.midWareSubMqttTopics:
        print(item)
        mc.m_sub(item)



#运行主函数
main()

