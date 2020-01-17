class Loginer(object):
    name="unkown"           #用户名
    id=123456               #用户id
    heartRestore=60        #心跳数量
    passwd="123456"         #用户密码

    def __init__(self,name_,heartRestore_=60):
        self.name=name_
        self.heartRestore=heartRestore_