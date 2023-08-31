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

import os
from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
is_testing = os.getenv(r'TESTING') != None
print("is_testing :",is_testing)

from discord.ext import commands, tasks
# intents = discord.Intents.default()
intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = "$", intents=intents)
# commands.Bot 繼承自 discord.Client

# 最後才 import 自己的 library
from Remind import Remind
from My_discord_functions import *
from util import *
set_bot(bot)

import datetime as datetimeLib
class Bot_status(commands.Cog):
    def __init__(self):
        self.reset.start()
        self.go_to_sleep = Go_to_sleep(bot)
        self.random_pic = Random_pic()

    # @tasks.loop(seconds=5.0) # 要記得 start 才會開始 loop
    reset_time = datetimeLib.time(hour=2, minute=1, tzinfo=datetimeLib.timezone.utc) # 不能用 pytz 的 timezone 會跳 WARNING !!
    @tasks.loop(time = reset_time)
    async def reset(self):
        print("reset")
        await self.do_everyday()
        print("reset finish")

    async def do_everyday(self):
        await send_anniversary(get_anniversary_days())
        await self.random_pic.daily_drive_pic()
        self.go_to_sleep.reset_sleep()

@bot.event
async def on_ready(): #當機器人完成啟動時
    print('目前登入身份：', bot.user)
    global mem
    mem = Bot_status()
    if is_testing : 
        await mem.reset()
    await bot.add_cog(mem.go_to_sleep)
    await bot.add_cog(mem.random_pic)
    await bot.add_cog(Remind(bot))
    await bot.add_cog(All_help())
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")

class All_help(commands.Cog):
    @app_commands.command(name = "help_all", description = "列出所有指令")
    async def help_all(self, interaction: Interaction):
        all_help_str = "\n".join(get_help(each_func) 
                for each_func in [Random_pic,Remind])
        await interaction.response.send_message(all_help_str)

        # all_help_str = "\n".join(each_func.get_help() for each_func in [
        #     Random_pic,Remind])
        # await interaction.response.send_message(all_help_str)

# 因為有使用 command 所以這裡不能夠使用
# @bot.event
# async def on_message(message): #當有訊息時
#     # print(dir(message))
#     print(message.author, message.content, message.created_at)
#     # print(dir(message.channel))
#     # print(message.channel.id)

#     #排除自己的訊息，避免陷入無限循環
#     if message.author == bot.user:
#         return  

# @bot.event
# async def on_member_join(member):  #新成員加入時觸發(尚未驗證)
#     pass

TOKEN = os.getenv(r'TOKEN')
print("TOKEN :", TOKEN)
# import keep_alive
# keep_alive.keep_alive()
bot.run(TOKEN)
print("bot offline")
