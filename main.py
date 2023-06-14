# coding:utf-8

import os

os.system("")

from dotenv import load_dotenv
import discord
import time


#紀錄狀態
class Memery():
  def __init__(self):
    self.reset()

  def reset(self):
    print("reset")
    self.sleep_time = 23
    self.good_night = 0
    self.good_night_str = [
      "超過 " + str(self.sleep_time) + " 點了, 快去睡覺",
      '妳給我睡覺喔! 😡'
    ]


mem = Memery()

# 狀態每天重置
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone="Asia/Taipei")
# schedule.every().day.at("04:00").do(mem.reset)
scheduler.add_job(mem.reset, 'cron', day_of_week='0-4', hour=4, minute=0)
scheduler.start()

# 讀取設定
load_dotenv(r"./settings/.env")
TOKEN = os.getenv(r'TOKEN')
print("TOKEN :", TOKEN)

#使用client class
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)
# client = discord.Client()



#調用event函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
  print('目前登入身份：', client.user)


@client.event
#當有訊息時
async def on_message(message):
  print(message.author, message.content)

  #排除自己的訊息，避免陷入無限循環
  if message.author == client.user:
    return

  # if "#2876" in str(message.author) :
  if "#5670" in str(message.author):
    if '不愛你' in message.content:
      await message.channel.send('但是我還很愛你')
    if '分手' in message.content:
      await message.channel.send('別想了! 反正我是不會答應的!')

    now_hour = time.localtime(time.time()).tm_hour
    if mem.good_night < len(mem.good_night_str) and (now_hour >= mem.sleep_time
                                                     or now_hour <= 4):
      await message.channel.send(mem.good_night_str[mem.good_night])
      mem.good_night += 1

#新成員加入時觸發(尚未驗證)
@client.event
async def on_member_join(member):
  pass
  # 目前不會用到，因為看到所以先記錄一下
  # guild = client.get_guild(GUILD_ID)
    # for channel in guild.channels:
    #     if channel.name == '一般':#<<記得改"一般"
    #         await channel.send(f"<@{member.id}> 你好呀:sunglasses:  請輸入你的遊戲ID，管理員看到就會把你加進公會~")

client.run(TOKEN)
