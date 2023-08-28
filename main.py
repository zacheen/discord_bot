# coding:utf-8

# python version 3.10 (python 3.7 無法安裝 discord 2.3.0 版)
# pip install -U discord.py
# pip install -U python-dotenv
# pip install apscheduler
# pip install Flask
# pip install pytz
# pip install requests
# pip install beautifulsoup4

import discord
# 一些常用 function 整理
# < 訊息相關 >
    # 發送訊息 : Channel.send()
    # 回復訊息 : Message.reply()
    # < 回覆內容 >
        # 嵌入訊息 : discord.Embed(description="", url=)
            # 主要用於回覆一大堆的文字，並且可附圖
        # 傳送檔案 : discord.File()

import time
import datetime as datetimeLib
from datetime import datetime
import pytz

import os
from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
MY_DISCORD_ID = os.getenv(r'MY_DISCORD_ID')
print("MY_DISCORD_ID :", MY_DISCORD_ID)

# testing settings
is_testing = os.getenv(r'TESTING') != None
print("is_testing :",is_testing)

# 最後才 import 自己的 library
from Remind import *
from My_discord_functions import *
# import My_discord_functions

from discord.ext import commands, tasks
#紀錄狀態
class Bot_status(commands.Cog):
    def __init__(self):
        self.reset.start()
        self.go_to_sleep = Go_to_sleep()

    # def cog_unload(self):
    #     print("execute cog_unload !!!!!!!!!!")
    #     self.reset.cancel()

    # @tasks.loop(seconds=5.0) # 要記得 start 才會開始 loop
    reset_time = datetimeLib.time(hour=1, minute=22, tzinfo=datetimeLib.timezone.utc) # 不能用 pytz 的 timezone 會跳 WARNING !!
    @tasks.loop(time = reset_time)
    async def reset(self):
        print("reset")
        await self.do_everyday()
        print("reset finish")

    async def do_everyday(self):
        await send_anniversary(get_anniversary_days())
        await send_drive_image()
        self.go_to_sleep.reset_sleep()

#使用client class
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)
set_client(client)

#調用event函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
    print('目前登入身份：', client.user)
    global mem
    mem = Bot_status()
    if is_testing : 
        await mem.reset()

@client.event
#當有訊息時
async def on_message(message):
    # print(dir(message))
    print(message.author, message.content, message.created_at)
    # print(dir(message.channel))
    # print(message.channel.id)

    #排除自己的訊息，避免陷入無限循環
    if message.author == client.user:
        return

    # 20230615 有更新 id 要注意
    if is_testing or MY_DISCORD_ID not in str(message.author):
    # if "zacheen" in str(message.author):
        if '不愛你' in message.content:
            await message.channel.send('但是我還很愛你')
        elif '愛你' in message.content:
            await message.reply('請當面告訴帥寶貝')
        if '分手' in message.content:
            await message.reply('別想了! 反正我是不會答應的!')

        baby_time = datetime.now(pytz.timezone("America/Los_Angeles"))
        ret_str = mem.go_to_sleep.tell_go_to_sleep(baby_time)
        if ret_str != None :
            await message.channel.send(ret_str)

    # 提醒事項
    if Remind.add_rem in message.content:
        try :
            to_add_mess = message.content.replace(Remind.add_rem,"").strip()
            Remind.add_item(message.channel, to_add_mess)
            await message.reply("成功紀錄 : "+to_add_mess)
        except :
            await message.reply("加入失敗")
    elif Remind.remove_rem in message.content:
        try :
            to_remove_mess = int(message.content.replace(Remind.remove_rem,"").strip())
            Remind.del_indx(message.channel, to_remove_mess)
            await message.reply("刪除結果 :\n" + Remind.get_rem(message.channel))
        except :
            await message.reply("移除失敗")
    elif Remind.list_rem in message.content:
        await message.reply(Remind.get_rem(message.channel))
    elif Remind.list_all_rem in message.content:
        await message.reply(Remind.get_all_rem())
    if "help" == message.content :
        await message.reply(Remind.get_help())


#新成員加入時觸發(尚未驗證)
@client.event
async def on_member_join(member):
    pass
    # 目前不會用到，因為看到所以先記錄一下
    # guild = client.get_guild(GUILD_ID)
        # for channel in guild.channels:
        #     if channel.name == '一般':#<<記得改"一般"
        #         await channel.send(f"<@{member.id}> 你好呀:sunglasses:  請輸入你的遊戲ID，管理員看到就會把你加進公會~")

TOKEN = os.getenv(r'TOKEN')
print("TOKEN :", TOKEN)
# import keep_alive
# keep_alive.keep_alive()
client.run(TOKEN)
print("client offline")
