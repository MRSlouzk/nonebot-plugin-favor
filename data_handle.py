import json
import os
import platform
import random

from nonebot.log import logger
# data_dir = "./data/favor" # ubuntu环境
class Vividict(dict): #多层嵌套字典
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

# scheduler = require("nonebot_plugin_apscheduler").scheduler

if(platform.system()=="Windows"):
    data_dir = "."
elif(platform.system()=="Linux"):
    data_dir = "./data/favor"
else:
    data_dir = "./data/favor"

def addNewType(uid: str,gid: str,type: str): #添加新数据类型
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
    content[uid][gid].update({f"{type}":0})
    with open(data_dir + "/favor.json", 'w') as f_new:
        json.dump(content, f_new, indent=4)

def initData(uid: str,gid: str): #初始化好感度
    data=Vividict()
    data[uid][gid]={}
    addNewType(uid,gid,"Favor") #好感度
    addNewType(uid, gid, "Today") #今日好感度增加量
    addNewType(uid, gid, "DialogAdd") #对话好感度增加量
    # with open(data_dir + "/favor.json", "r") as f:
    #     content = json.load(f)
    # content.update(data)
    # with open(data_dir + "/favor.json", 'w') as f_new:
    #     json.dump(content,f_new,indent=4)
    #     f_new.close()

def init_today(): #初始化每日数值
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
    for keys,values in content.items():
        values["684869122"]["Today"]=0
        values["684869122"]["DialogAdd"] = 0
    with open(data_dir + "/favor.json", 'w') as f_new:
        json.dump(content, f_new, indent=4)

def changeData(uid: str,gid: str,favor: int): #修改好感度
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
        try:
            content[uid][gid]["Favor"]=favor
            with open(data_dir + "/favor.json", 'w') as f_new:
                json.dump(content,f_new,indent=4)
        except KeyError:
            initData(uid,gid)
            changeData(uid,gid,favor)

def changeTargetData(uid: str,gid: str,type: str,value: int): #修改指定数值
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
        try:
            content[uid][gid][f"{type}"]=value
            with open(data_dir + "/favor.json", 'w') as f_new:
                json.dump(content,f_new,indent=4)
        except KeyError:
            initData(uid,gid)
            changeTargetData(uid,gid,type,value)

def readData(uid: str,gid: str) -> int : #读取好感度
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
    try:
        return int(content[uid][gid]["Favor"])
    except:
        initData(uid, gid)
        readData(uid,gid)

def readMaxData(uid: str,gid: str) -> int : #读取今日变化好感度
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
    try:
        return int(content[uid][gid]["Today"])
    except KeyError:
        initData(uid, gid)
        readMaxData(uid,gid)

def readTargetData(uid: str,gid: str,type: str) -> int: #读取指定类型数据
    with open(data_dir + "/favor.json", "r") as f:
        content = json.load(f)
    try:
        return int(content[uid][gid][f"{type}"])
    except KeyError:
        initData(uid, gid)
        readTargetData(uid,gid,type)

def addData(uid: str,gid: str,favor: int): #增加好感度
    try:
        value=readMaxData(uid,gid)+favor
        if (value <= 15):
            if(readData(uid,gid)+favor>0 and readData(uid,gid)+favor<1000):
                with open(data_dir + "/favor.json", "r") as f:
                    content = json.load(f)
                content[uid][gid]["Favor"] += favor
                content[uid][gid]["Today"] += favor
                with open(data_dir + "/favor.json", 'w') as f_new:
                    json.dump(content, f_new, indent=4)
                logger.info(f"{int(uid)}的好感度增加了{favor}!")
            else:
                logger.warning(f"{int(uid)}的好感度已经超出范围!")
        else:
            logger.warning(f"{int(uid)}今日好感度增加量已到达上限!")
    except KeyError:
        initData(uid,gid)
        addData(uid,gid,favor)

def addTargetData(uid: str,gid: str,type: str,value: int): #增加好感度
    try:
        with open(data_dir + "/favor.json", "r") as f:
            content = json.load(f)
        content[uid][gid][f"{type}"] += value
        with open(data_dir + "/favor.json", 'w') as f_new:
            json.dump(content, f_new, indent=4)
        logger.info(f"{int(uid)}的{type}增加了{value}!!!")
    except KeyError:
        initData(uid,gid)
        addTargetData(uid,gid,value)

def randomDataChange(uid: str,gid: str,type: int): #好感度随机变化
    if(type==0):
        choice=random.randint(-1,3)
    elif(type==1):
        choice=random.randint(-2,2)
    elif(type==3):
        choice=random.randint(0,3)
    else:
        choice = random.randint(-2, 2)
    addData(uid,gid,choice)

# if __name__=="__main__":
#     addNewType("3237231778","684869122","DialogMax")
#     print(readTargetData("3237231778","684869122","DialogMax"))
#     initData("32372317780","684869122",0)
#     initData("3237","684869122",0)
#     initData("114514","684869122",0)
#     addData("32372317780","684869122",3)
#     addData("3237","684869122",3)
#     init_today()