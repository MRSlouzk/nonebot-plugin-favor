# Python Script Created by MRS
import json
import os
import platform
import random
from datetime import date

from nonebot.log import logger

from .items_list import *
# from items_list import *

class Vividict(dict): #多层嵌套字典
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

if(platform.system()=="Windows"):
    data_dir = "."
elif(platform.system()=="Linux"):
    data_dir = "./data/favor"
else:
    data_dir = "./data/favor"

def initData_i(uid: str): #背包
    data=Vividict()
    data[uid]={}
    with open(data_dir + "/items.json", "r") as f:
        content = json.load(f)
    content.update(data)
    with open(data_dir + "/items.json", 'w') as f_new:
        json.dump(content,f_new,indent=4)

def get_item_list(uid: str):
    with open(data_dir + "/items.json", "r",encoding="utf-8") as f:
        content = json.load(f)
    items=content[uid]
    if(items=={}):
        return -1
    else:
        return items

def add_item(uid: str,item: dict):
    with open(data_dir + "/items.json", "r",encoding="utf-8") as f:
        content = json.load(f)
    content[uid].update(item)
    with open(data_dir + "/items.json", 'w',encoding="utf-8") as f_new:
        json.dump(content,f_new,indent=4)

def add_item_num(uid: str,item: dict,num: int):   # 增加物品数量
    global name
    lst=get_item_list(uid)
    if(lst!=-1):
        for i in item.keys():
            name=i
            break
        for keys in lst:
            if(name==keys):
                with open(data_dir + "/items.json", "r", encoding="utf-8") as f:
                    content = json.load(f)
                if (content[uid][name]["number"] + num <= 0):
                    content[uid].pop(name)
                else:
                    content[uid][name]["number"] += num
                with open(data_dir + "/items.json", 'w', encoding="utf-8") as f_new:
                    json.dump(content, f_new, indent=4)
                return
        add_item(uid,item)
    else:
        add_item(uid, item)
        return

def random_item(level: int=0): #随机抽取物品
    result=random.randint(1,600)
    # return result
    if(result<=10):
        return cake
    elif(result>10 and result<= 35):
        return cake1
    elif (result > 35 and result <= 75):
        return cake2
    elif (result > 75 and result <= 85):
        return bear
    elif (result > 85 and result <= 110):
        return bear1
    elif (result > 110 and result <= 150):
        return bear2
    else:
        return -1

if __name__ == "__main__":
    pass
    # pass
    # initData_i("3237231778")
    # dic={"蛋糕":{"数量":1,"品质":"优"}}
    # add_item("3237231778",cake)
    # print(get_item_list("3237231778"))

    # add_item_num("3237231778",cake,1)

    # print(get_item_list("3237231778"))

    # lst=content.keys()
    # print(lst[0])
    # for keys in content:
    #     initData_i(keys)