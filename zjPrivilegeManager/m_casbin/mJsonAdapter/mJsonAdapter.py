#-*- coding: utf-8 -*-


import casbin
import json
import os
from casbin import persist

class CasbinRule(object):

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

        return text

    def __repr__(self):
        return '<CasbinRule :"{}">'.format(str(self))

class jsonAdapter(persist.Adapter):

    pfpath='none.json'
    storeJs=json.loads("{}")
    def __init__(self,  policyFilePath):
        self.pfpath=policyFilePath


    def load_policy(self, model):

        fd=open(self.pfpath,mode='r',encoding='utf-8')
        str=fd.read()

        fd.close()
        self.storeJs=json.loads(str)

        casbinRuleStrct = []
        for item in self.storeJs:
            cr=CasbinRule(item['PType'],
                          item['V0'],item['V1'],
                          '','',
                          '', '')
            if item.get('V2'):
                cr.v2=item['V2']
            if item.get('V3'):
                cr.v2=item['V3']
            if item.get('V4'):
                cr.v2=item['V4']
            if item.get('V5'):
                cr.v2 = item['V5']

            persist.load_policy_line(cr.load(),model)

    def _save_policy_line(self, ptype, rule):
        csbr = CasbinRule()
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
        flag = 0
        for item in self.storeJs:
            if (item==js):
                flag=1
                break
        if (flag==0):
            self.storeJs.append(js)


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
        fd = open(self.pfpath, mode='w+')
        fd.write(json.dumps(self.storeJs))
        fd.close()
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
