
from pymongo import MongoClient
import threading
import datetime
from login.loginer import *
import json
import time



USR_HAVE_EXIST="userNameHaveExist"              #用户名已经存在
PASSWD_ERROR="passwdErr"                        #密码错误
LOGIN_OK="loginOk"                              #登录成功
USR_UN_EXIST="loginUserNameUnExist"             #登录用户名不存在
REGISTER_OK="registerOk"                        #注册成功

NONE_USR_NAME ="loginNoUserName"                #登录没有用户名
NONE_PASSWD ="loginNoPasswd"                    #登录没有密码



USR_NOT_LOGNIN ="updateHeartUserNotOnline"      #更新的心跳的用户都没有在线

UPDATE_HEART_OK="updateHeartOk"                 #更新心跳成功


LOGIN_TYPE="loginType"      #操作键值

LOGIN_TYPE_LOGIN    = "login"       #登录操作
LOGIN_TYPE_HEART    = "heart"       #心跳操作
LOGIN_TYPE_REGISTER = "register"    #注册操作

LOGIN_TYPE_ERR="loginTypeErr"            #登录相关类型错误,不是上面的操作中的一种


class LoginManager:
    usrList=dict()                      #所有登录在线的用户列表
    heartUpdateInterval=2               #更新心跳的时间间隔
    latestHeartNum=60                   #心跳更新后心跳满值
    heartStep=5                         #每个间隔时间心跳减小值

    mongoDbName="权限管理模块"
    mongoDbCol="login"
    mongodConnectStr = 'mongodb://127.0.0.1:27017/'
    dbClient=None
    dbCollection=None

    usrListMutex=threading.Lock()





    def __init__(self,url='mongodb://127.0.0.1:27017/'
                 ,latestHeartNum_=60,
                 heartStep_=5,
                 heartUpdateInterval_=2):

        self.mongodConnectStr=url
        self.latestHeartNum=latestHeartNum_
        self.heartStep=heartStep_
        self.heartUpdateInterval=heartUpdateInterval_


        self.usrList["ywh"]=Loginer("ywh",20)
        self.usrList["lyf"]=Loginer("lyf",14)




    def connectDb(self):
        try:
            self.dbClient=MongoClient(self.mongodConnectStr)
            db=self.dbClient.get_database(self.mongoDbName)
            self.dbCollection=db.get_collection(self.mongoDbCol)
            print("Mongdb 连接成功")
        except:
            dbCollection=None
            print("Mongdb 连接失败")


    def run(self):
        print("运行 心跳更新循环")
        while True:

            self.usrListMutex.acquire()

            for key in list(self.usrList):
                if(self.usrList[key].heartRestore==None):
                    self.usrList.pop(key)
                    continue
                self.usrList[key].heartRestore=self.usrList[key].heartRestore-self.heartStep
                if(self.usrList[key].heartRestore<=0):
                    if(key!=self.usrList[key].name):
                        print("用户名键值存储出现问题")
                        self.usrList.pop(key)
                    else:
                        print(self.usrList[key].name, " 用户掉线退出了登录")
                        self.usrList.pop(key)


            self.usrListMutex.release()
            #print("time lost ")
            time.sleep(self.heartUpdateInterval)


    def loginNewUsr(self,usrName,passwd):

        if(usrName==""):
            return NONE_USR_NAME
        if(passwd==""):
            return NONE_PASSWD

        query={}
        query["用户名"]=usrName

        cursor=self.dbCollection.find(query)
        n=0
        for item in cursor:
            n=n+1

        cursor.close()

        if(n==0):
            return USR_UN_EXIST
        else:
            js=self.dbCollection.find_one(query)
            if(js.get("密码") and js["密码"]==passwd):
                self.addUsrToUsrList(usrName)
                return LOGIN_OK
            else:
                return PASSWD_ERROR

    def addUsrToUsrList(self,usrName):

        self.usrListMutex.acquire()

        if(not self.usrList.get(usrName)):
            self.usrList[usrName] = Loginer(usrName,self.latestHeartNum)
            print("用户: ",usrName," 登录了!")
        else:
            self.usrList[usrName].heartRestore=self.latestHeartNum

        self.usrListMutex.release()


    def registerNewUsr(self,usrName,passwd,other=""):
        query={}
        query["用户名"]=usrName

        if(usrName==""):
            return NONE_USR_NAME
        if(passwd==""):
            return NONE_PASSWD

        cursor=self.dbCollection.find(query)

        n=0
        for item in cursor:
            n=n+1
        cursor.close()


        if(n!=0):
            return USR_HAVE_EXIST
        else:
            updateJs={}
            updateJs["用户名"]=usrName
            updateJs["密码"]=passwd
            updateJs["更新时间"]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updateJs["其他"]=other
            self.dbCollection.insert(updateJs)
            return REGISTER_OK



    def updateHeart(self,userName):
        self.usrListMutex.acquire()

        if (self.usrList.get(userName)):
            self.usrList[userName].heartRestore=self.latestHeartNum

            self.usrListMutex.release()
            return UPDATE_HEART_OK
        else:
            self.usrListMutex.release()
            return USR_NOT_LOGNIN



    def getJsStr(self,js=json.loads("{}"), key="none"):
        if key in js:
            return js[key]
        else:
            return ""


    def jsMessageDeal(self,js):
        if (not js.get(LOGIN_TYPE)):
            return LOGIN_TYPE_ERR
        userName=""
        passwd=""
        other=""
        userName=self.getJsStr(js,"userName")
        passwd=self.getJsStr(js,"passwd")
        other=self.getJsStr(js,"other")

        if(js[LOGIN_TYPE]==LOGIN_TYPE_LOGIN):
            return (self.loginNewUsr(userName,passwd))
        if(js[LOGIN_TYPE]==LOGIN_TYPE_HEART):
            return (self.updateHeart(userName))
        if (js[LOGIN_TYPE] == LOGIN_TYPE_REGISTER):
            return (self.registerNewUsr(userName,passwd,other))

        return LOGIN_TYPE_ERR





def test():
    lgm=LoginManager()
    lgm.connectDb()
    print (lgm.registerNewUsr("余汪海","zhijintech","QQ:2433022001"))
    print (lgm.registerNewUsr("全能骑士","nopass"))

    print(lgm.loginNewUsr("余汪海","zhijintech"))
    #print(lgm.loginNewUsr("余汪海","zhijintech"))

    js={}
    js[LOGIN_TYPE]=LOGIN_TYPE_HEART
    js["userName"]="余汪海"
    js["passwd"]="zhijintech"

    print(lgm.jsMessageDeal(js))


    lgm.updateHeart("lyf")
    lgm.run()


#test()