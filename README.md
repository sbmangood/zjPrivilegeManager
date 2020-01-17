# zjPrivilegeManager
权限管理模块
自己做的一个基于pycasbin 开源库 mqtt作为中间件  带登录功能的 权限管理后台程序 数据存储mongodb数据库

使用数据流:
1.Client 端登录权限管理模块
2.Client不直接向Server端发送各种数据请求,而是发送给权限管理模块,权限管理只处理在线Client 的数据请求
3.权限管理模块筛选Client用户的各种数据权限,有权限的再转发给Server端
4.Server 直接向Client发送数据

 
