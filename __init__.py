from email import message
import json
import random
import re
from typing import List,Literal

from nonebot import on_command,on_keyword,on_message
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageEvent,Message,Bot,MessageSegment
from nonebot.log import logger
from nonebot.params import CommandArg

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

from .data_handle import * #导入数据处理包
from .items_handle import * #导入物品包

strange_text=["我们之前是不是没见过呀?","凛绪不认识你呀!","爸爸妈妈说要远离陌生人!","别靠近凛绪!","你是谁呀?","凛绪不和陌生人打招呼!"]
familiar_text=["你好啊","凛绪之前好像见过你!","(微笑)"]
known_text=["你是凛绪的好朋友!","有什么困难凛绪会帮你的!"]
friends_text=["(贴上来)","凛绪好开心能和你一起!","很高兴认识你!"]
family_text=["凛绪要抱抱!","[CQ:at,qq={event.user_id}]是凛绪最重要的家人!","凛绪喜欢你!","凛绪也爱你!"]

def text(value): #输出语句
    if(value<20):
        return random.choice(strange_text)
    elif(value<100):
        return random.choice(family_text)
    elif (value < 500):
        return random.choice(known_text)
    elif(value<800):
        return random.choice(friends_text)
    elif(value<=1000):
        return random.choice(family_text)

##基础功能实现##

def _checker(event: MessageEvent) -> bool:
    return (event.message_type=="private")

query=on_command("好感度",priority=50,block=True)
reset=on_command("计数清零",priority=50,block=False,permission=SUPERUSER)
set=on_command("设置好感度",priority=50,block=False,permission=SUPERUSER)
help=on_command("好感度帮助",priority=50,block=True)
register=on_command("注册好感度",priority=49,block=False)
rank=on_command("好感度排名",priority=50,block=False)

def _check(event:GroupMessageEvent):
    return event.group_id==684869122

@query.handle()
async def _(event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    value=readData(uid,gid)
    if(value!=-1):
        if(event.user_id==341163964):
            await query.finish(Message(f"[CQ:at,qq=341163964]凛绪最爱妈妈了!!!"))
        await query.finish(Message(f"[CQ:at,qq={event.user_id}]凛绪对你的好感度为{value}呀!{text(int(value))}"))
    else:
        await query.finish(Message("还没有注册好感度啊!输入/注册好感度 后才可以使用好感度系统!"))

@reset.handle()
async def _(event: PrivateMessageEvent):
    if(event.user_id==3237231778):
        init_today()
        await reset.finish("清零完成!")
    logger.warning("有人要篡改数据!")
    await reset.finish("没有权限啊!")

@set.handle()
async def _(event: PrivateMessageEvent,args: Message = CommandArg()):
    arg = args.extract_plain_text().split()
    if(len(arg)==2):
        if(event.user_id==3237231778):
            if(changeData(arg[0],"684869122",int(arg[1]))!=-1):
                await reset.finish("设置完成!")
            else:
                await reset.finish("请先注册该用户!")
        await reset.finish("没有权限啊!")
    await reset.finish()

@help.handle()
async def _(args: Message = CommandArg()):
    arg = args.extract_plain_text().split()
    if(len(arg)==0):
        await help.finish(Message(f"每天戳戳凛绪或者夸夸凛绪都可以增加好感度!但是要注意凛绪的心情!心情不好的时候有些行为可能会倒扣好感度的!"))
    elif(len(arg)==1):
        if(arg[0]=="抽奖"):
            await help.finish(Message("抽奖系统:输入/抽取道具 来进行抽取，每日都增加一次次数。1%获取优等级玩具熊或者蛋糕,2.5%获取良,4%获取劣"))
        else:
            await help.finish(Message("无效参数!"))
    else:
        await help.finish(Message("无效参数!"))

@register.handle()
async def _(event:GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    if readData(uid,gid)==-1:
        initData(uid,gid)
        await register.finish(Message(f"[CQ:at,qq={event.user_id}] /好感度 查看凛绪对你的好感度哦"))
    else:
        await register.finish(Message(f"[CQ:at,qq={event.user_id}]已经注册过了啊!"))

@rank.handle()
async def _(bot:Bot,event:GroupMessageEvent):
    json=raw_json()
    count=0
    msg=Message()
    sort_json = sorted(json.items(), key=lambda x: x[1]["684869122"]['Favor'], reverse=True)
    for keys,values in sort_json:
        if(count==8):
            break
        count+=1
        info=await bot.get_group_member_info(group_id=event.group_id,user_id=int(keys),no_cache=False)
        card=info.get("card")
        if(card==''):
            card=info.get("nickname")
        dict_new=values
        for i in dict_new.items():
            favor=i[1]["Favor"]
            msg+=Message(f"{count}.{card}(qq:{keys}):{favor}\n")
    if(message!= ""):
        await rank.finish(msg)
    else:
        await rank.finish("数据错误！")


inventory=on_command("查看背包",priority=50,block=False)
times_q=on_command("查询剩余次数",priority=50,block=False)
extract=on_command("抽取道具",priority=50,block=False)

@extract.handle()
async def _(event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    if(readTargetData(uid,gid,"Extract")<=0):
        await extract.finish(MessageSegment.at(event.user_id)+Message("抽奖次数用完了!"))
    item_get=random_item()
    if(item_get==-1):
        addTargetData(uid, gid, "Extract", -1)
        await extract.finish(MessageSegment.at(event.user_id)+Message("很遗憾没抽到东西呀!"))
    else:
        addTargetData(uid,gid,"Extract",-1)
        add_item_num(uid,item_get,1)
        for i in item_get.keys():
            await extract.finish(MessageSegment.at(event.user_id)+Message("恭喜抽到奖品:"+i))

@inventory.handle()
async def _(event: GroupMessageEvent):
    lst=get_item_list(str(event.user_id))
    if(lst==-1):
        await inventory.finish(MessageSegment.at(event.user_id)+Message("背包里没有物品!"))
    else:
        msg=Message()
        for j in lst.keys():
            for i in lst.values():
                numb=i["number"]
                msg+=Message(f"{j},数量:{numb}\n")
                break
        await inventory.finish(MessageSegment.at(event.user_id)+msg)

@times_q.handle()
async def _(event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    value=readTargetData(uid,gid,"Extract")
    await times_q.finish(MessageSegment.at(event.user_id)+Message(f"次数剩余:{value}"))

##凛绪每日心情

def _checker1(event: GroupMessageEvent) ->bool :
    return (event.message_type=="group")

mood_d=on_keyword({"凛绪今天心情怎么样"},rule=_checker1,priority=98)

def mood_text(mood: int):
    if(mood<=20):
        return "凛绪今天不开心!不要惹凛绪生气!"
    elif(mood<=40):
        return "凛绪今天心情不太好......"
    elif(mood<=60):
        return "凛绪今天棒棒哒~"
    elif(mood<=80):
        return "凛绪想要一起玩!"
    elif(mood<=100):
        return "凛绪今天好开心呀!!!"

@mood_d.handle()
async def _():
    mood=mood_daliy()
    logger.info(f"今日心情值:{mood_daliy()}")
    await mood_d.finish(Message(f"{mood_text(mood)}"))

##提升好感度 法一##
#此方法不用 @凛绪

word_set={"凛绪可爱","喜欢凛绪","摸摸凛绪","抱抱凛绪","凛绪乖"}

fav_up=on_keyword(word_set,rule=_checker1,priority=98)

@fav_up.handle()
async def _(event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    rnd_favor=random.randint(0,2)
    now_value = readTargetData(uid, gid, "DialogAdd")
    if(now_value!=-1):
        if now_value<=5:
            addData(uid,gid,rnd_favor)
            logger.info(f"凛绪对{uid}的好感度增加了{rnd_favor}!")
        else:
            logger.warning(f"{uid}的今日通过会话提升的好感度到上限了!")
        await fav_up.finish()
    else:
        await fav_up.finish(Message("好感度没注册呢!"))

##提升好感度 法二##
#此方法需要 @凛绪

trigger_text_1=["摸","抱","亲","喂","可爱","喜欢你"]
trigger_text_2=["滚","爬","走啊"]

def favor_dialog_rule(event: GroupMessageEvent) -> bool: #触发器规则函数
    tem_jud=False
    all_list=trigger_text_1+trigger_text_2
    is_tme="[CQ:at,qq=3223808209]" in event.raw_message
    for items in range(0,len(all_list)):
        if(all_list[items] in event.raw_message):
            tem_jud=True
    return (tem_jud and is_tme)

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
async def _(event: GroupMessageEvent):
    uid=str(event.user_id)
    gid=str(event.group_id)
    message=re.sub(u"\\[.*?]", "", event.raw_message) #提取原始消息并去除CQ消息段
    value=readTargetData(uid,gid,"DialogAdd")
    if(value!=-1):
        # logger.info(f"{event.raw_message}")
        if(ergodic_list(trigger_text_1,message) and int(value)<=1):
            rnd=random.randint(1,3)
            await favor_trigger.send(Message("凛绪好开心!"))
            addData(uid,gid,rnd)
            addTargetData(uid,gid,"DialogAdd",1)
        elif(ergodic_list(trigger_text_2,message) and int(value)<=1):
            rnd=random.randint(-3,-1)
            await favor_trigger.send(Message("凛绪好难过......"))
            addData(uid,gid,rnd)
            addTargetData(uid,gid,"DialogAdd",1)
        else:
            await favor_trigger.finish(Message("谢谢......"))
    else:
        await favor_trigger.finish(Message("请先注册好感度!"))
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

executor = {
    'default': ThreadPoolExecutor(1)  # 只能有1个线程存在
}

backgroundScheduler = BackgroundScheduler(executors=executor)
cornTrigger = CronTrigger(hour=0, minute=0, second=0)
backgroundScheduler.add_job(init_today, cornTrigger, id='reset_favor_data_daily')
backgroundScheduler.start()
