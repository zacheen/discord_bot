import os
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
      "超過 " + str(self.sleep_time) + " 點了, 快去睡覺", '妳給我睡覺喔! 😡'
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
client = discord.Client()


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


client.run(TOKEN)
