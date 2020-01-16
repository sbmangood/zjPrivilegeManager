import pymongo
from pymongo import MongoClient

import casbin
import json
import os
from casbin import persist


m_mongoDbName="权限管理模块"
m_mongoDbCol="casbinCol"

class CasbinRule_(object):

    __tablename__ = "casbin_rule"
    def __init__(self,PType_='',v0_='',
                 v1_='',v2_='',v3_='',
                 v4_='',v5_=''):
        self.PType=PType_
        self.v0=v0_
        self.v1=v1_
        self.v2=v2_
        self.v3=v3_
        self.v4=v4_
        self.v5=v5_

    def load(self):
        text = self.PType
        if self.v0!='':
            text = text+', '+self.v0
        if self.v1!='':
            text = text+', '+self.v1
        if self.v2!='':
            text = text+', '+self.v2
        if self.v3!='':
            text = text+', '+self.v3
        if self.v4!='':
            text = text+', '+self.v4
        if self.v5!='':
            text = text+', '+self.v5

        print (text)
        return text


    def __repr__(self):
        return '<CasbinRule :"{}">'.format(str(self))

class MongoAdapter(persist.Adapter):

    mongodConnectStr='mongodb://127.0.0.1:27017/'
    dbClient=None
    dbCollection=None
    dbItemList=[]

    def __init__(self,  str='mongodb://127.0.0.1:27017/'):
        self.mongodConnectStr=str


    def connectDb(self):
        try:
            self.dbClient=MongoClient(self.mongodConnectStr)
            db=self.dbClient.get_database(m_mongoDbName)
            self.dbCollection=db.get_collection(m_mongoDbCol)

            print("Mongdb 连接成功")
        except:
            dbCollection=None
            print("Mongdb 连接失败")

    def load_policy(self, model):

        if (self.dbCollection!=None):
            cursor=self.dbCollection.find()
            for item in cursor:
                item.pop("_id")
                self.dbItemList.append(item)
                #print(item)
            cursor.close()

            #print(self.dbItemList)
            for it in self.dbItemList:
                cr=CasbinRule_()
                if it.get("PType"):
                    cr.PType=it["PType"]
                if it.get("V0"):
                    cr.v0=it["V0"]
                if it.get("V1"):
                    cr.v1=it["V1"]
                if it.get("V2"):
                    cr.v2=it["V2"]
                if it.get("V3"):
                    cr.v3=it["V3"]
                if it.get("V4"):
                    cr.v4=it["V4"]
                if it.get("V5"):
                    cr.v5=it["V5"]
                persist.load_policy_line(cr.load(),model)

        else:
            print("Mongdb 连接失败 无法 读取")



    def _save_policy_line(self, ptype, rule):
        csbr = CasbinRule_()
        csbr.PType=ptype
        if len(rule) > 0:
            csbr.v0 = rule[0]
        if len(rule) > 1:
            csbr.v1 = rule[1]
        if len(rule) > 2:
            csbr.v2 = rule[2]
        if len(rule) > 3:
            csbr.v3 = rule[3]
        if len(rule) > 4:
            csbr.v4 = rule[4]
        if len(rule) > 5:
            csbr.v5 = rule[5]
        self.saveCasbinRule(csbr)
    def saveCasbinRule(self,casbinRule):

        js=json.loads("{}")
        js["PType"]=casbinRule.PType
        if(casbinRule.v0!=''):
            js['V0']=casbinRule.v0
        if(casbinRule.v1!=''):
            js['V1']=casbinRule.v1
        if(casbinRule.v2!=''):
            js['V2']=casbinRule.v2
        if(casbinRule.v3!=''):
            js['V3']=casbinRule.v3
        if(casbinRule.v4!=''):
            js['V4']=casbinRule.v4
        if(casbinRule.v5!=''):
            js['V5']=casbinRule.v5


        if js  not in self.dbItemList:
            self.dbItemList.append(js)
        print(self.dbItemList)
        for it in self.dbItemList:
            #
            if(it.get("_id")):
                it.pop("_id")
            #print(it)
            con={}
            con["$set"]=it;
            cursor = self.dbCollection.find(it)
            n=0
            for itt in cursor:
                n=n+1
            cursor.close()

            if(n==0):
                self.dbCollection.insert_one(it)
            else:
                self.dbCollection.update(it, con, multi=True)


            #print("test")








    def save_policy(self, model):
        '''
        implementing add Interface for casbin \n
        save the policy in mongodb \n
        '''
        for sec in ["p", "g"]:
            if sec not in model.model.keys():
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    self._save_policy_line(ptype, rule)

        return True

    def add_policy(self, sec, ptype, rule):
        """add policy rules to mongodb"""
        #self._save_policy_line(ptype, rule)

    def remove_policy(self, sec, ptype, rule):
        """delete policy rules from mongodb"""
        pass

    def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """
        delete policy rules for matching filters from mongodb
        """
        pass