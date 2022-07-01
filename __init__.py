import json
import random
import re
from typing import List,Literal

from nonebot import on_command,require,Bot,on_keyword,on_message
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageEvent,Message
from nonebot.log import logger
from nonebot.params import CommandArg
# sys.path.append("..")
# from favor import data_handle

from .data_handle import * #导入数据处理包

strange_text=["我们之前是不是没见过呀?","凛绪不认识你呀!","爸爸妈妈说要远离陌生人!"]
familiar_text=["你好啊","凛绪之前好像见过你!","(微笑)","(挥手)"]
friends_text=["(贴上来)","凛绪好开心能和你一起!","很高兴认识你!"]
family_text=["凛绪要抱抱!","[CQ:at,qq={event.user_id}]是凛绪最重要的家人!","凛绪喜欢你!","凛绪也爱你!"]

def text(value): #输出语句
    if(value<20):
        return strange_text[random.randint(0,2)]
    elif(value<100):
        return familiar_text[random.randint(0,3)]
    elif(value<800):
        return friends_text[random.randint(0,2)]
    elif(value<=1000):
        return family_text[random.randint(0,3)]

##基础功能实现##

def _checker(event: MessageEvent) -> bool:
    return (event.message_type=="private")

query=on_command("好感度",priority=50,block=True)
reset=on_command("计数清零",priority=50,block=False,permission=SUPERUSER)
set=on_command("设置好感度",priority=50,block=False,permission=SUPERUSER)
help=on_command("好感度帮助",priority=50,block=True)

@query.handle()
async def _(event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    value=readData(uid,gid)
    if(event.user_id==341163964):
        await query.finish(Message(f"[CQ:at,qq=341163964]凛绪最爱妈妈了!!!"))
    await query.finish(Message(f"[CQ:at,qq={event.user_id}]凛绪对你的好感度为{value}呀!{text(int(value))}"))

@reset.handle()
async def _(event: PrivateMessageEvent):
    if(event.user_id==3237231778):
        init_today()
        await reset.finish("清零完成!")
    await reset.finish("没有权限啊!")

@set.handle()
async def _(event: PrivateMessageEvent,args: Message = CommandArg()):
    arg = args.extract_plain_text().split()
    if(len(arg)==2):
        if(event.user_id==3237231778):
            changeData(arg[0],"684869122",int(arg[1]))
            await reset.finish("设置完成!")
        await reset.finish("没有权限啊!")
    await reset.finish()

@help.handle()
async def _(event:GroupMessageEvent):
    await help.finish(f"[CQ:at,qq={event.user_id}]")

##提升好感度 法一##
#此方法不用 @凛绪

word_set={"凛绪可爱","喜欢凛绪","摸摸凛绪"}

def _checker1(event: GroupMessageEvent) ->bool :
    return (event.message_type=="group")

fav_up=on_keyword(word_set,rule=_checker1,priority=98)

@fav_up.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    rnd_favor=random.randint(0,2)
    try:
        now_value=readTargetData(uid,gid,"DialogAdd")
    except KeyError:
        now_value=readTargetData(uid,gid,"DialogAdd")
    finally:
        now_value = readTargetData(uid, gid, "DialogAdd")
    if now_value<=5:
        addData(uid,gid,rnd_favor)
        logger.info(f"凛绪对{uid}的好感度增加了{rnd_favor}!")
    else:
        logger.warning(f"{uid}的今日通过会话提升的好感度到上限了!")
    await fav_up.finish()

##提升好感度 法二##
#此方法需要 @凛绪

trigger_text_1=["摸","抱","亲","喂"]
trigger_text_2=["滚","爬","走啊"]

def favor_dialog_rule(event: GroupMessageEvent) -> bool: #触发器规则函数
    tem_jud=False
    all_list=trigger_text_1+trigger_text_2
    for items in range(0,len(all_list)):
        if(all_list[items] in event.raw_message):
            tem_jud=True
    return (tem_jud and event.is_tome)

def ergodic_list(list_name: List[str],msg: str) -> bool: #遍历名为list_name的字符串列表判断msg是否在里面
    result=False
    try:
        length=len(list_name)
    except NameError:
        return False
    for items in range(0,length):
        if(list_name[items] in msg):
            result=True
    return result

favor_trigger=on_message(favor_dialog_rule,priority=97)

@favor_trigger.handle()
async def _(event: GroupMessageEvent,bot: Bot):
    uid=str(event.user_id)
    gid=str(event.group_id)
    message=re.sub(u"\\[.*?]", "", event.raw_message) #提取原始消息并去除CQ消息段
    # logger.info(f"{event.raw_message}")
    if(ergodic_list(trigger_text_1,message) and int(readTargetData(uid,gid,"DialogAdd"))<=1):
        rnd=random.randint(1,3)
        Message("凛绪好开心!")
        addData(uid,gid,rnd)
        addTargetData(uid,gid,"DialogAdd",1)
    elif(ergodic_list(trigger_text_2,message) and int(readTargetData(uid,gid,"DialogAdd"))<=1):
        rnd=random.randint(-3,-1)
        Message("凛绪好难过......")
        addData(uid,gid,rnd)
        addTargetData(uid,gid,"DialogAdd",1)
    await favor_trigger.finish()
# (未实现)每日零点清零好感度增加计数限制
"""
thread=Thread(target=init_today)
thread.start()
while(True):
    ehour = 0  # 定时小时
    emin = 0  # 定时分钟
    esec = 0  # 定时秒
    current_time = time.localtime(time.time())  # 当前时间date
    # 操作
    if ((current_time.tm_hour == ehour) and (current_time.tm_min == emin) and (current_time.tm_sec == esec)):
        with open(data_dir + "/favor.json", "r") as f:
            content = json.load(f)
        for items in content:
            items["684869122"]["Today"] = 0
        logger.info("清零完成!")
        # 调用相关方法：执行计算、发邮件动作。
        sleep(1)
"""
