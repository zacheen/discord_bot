# coding:utf-8

# python version 3.10 (python 3.7 無法安裝 discord 2.3.0 版)
# pip install -U discord.py
# pip install -U python-dotenv
# pip install apscheduler
# pip install Flask

import os
# os.system("")

from dotenv import load_dotenv
import discord
import time

#關鍵字
class Remind():
  add_rem = '加入提醒事項:'
  remove_rem = '刪除提醒事項:'
  list_rem = '列出提醒事項'
  all_command = [add_rem, remove_rem, list_rem, ]

  def get_help():
    help_str = "目前共有"+str(len(Remind.all_command))+"種指令\n    "
    help_str += "\n    ".join(Remind.all_command)
    return help_str
  
  def get_all_rem() :
    full_remind = ""
    with open(os.getenv(r'REMIND_PATH'),"r") as fr :
      for indx, each_remind in enumerate(fr.readlines(), 1):
        full_remind += str(indx)+". "+each_remind # each_remind 結尾已經有換行
    if full_remind == "" :
      full_remind = "沒有剩餘代辦事項"
    return full_remind

  def del_indx(tar_indx) : # indx start : 1
    remain_remind = ""
    with open(os.getenv(r'REMIND_PATH')) as fr :
      for indx, each_remind in enumerate(fr.readlines(), 1):
        if indx == tar_indx : 
          continue
        remain_remind += each_remind # each_remind 結尾已經有換行
    with open(os.getenv(r'REMIND_PATH'),"w") as fw :
      fw.write(remain_remind)
#紀錄狀態
class Memery():
  def __init__(self):
    self.reset()

  def reset(self):
    print("reset")
    self.sleep_time = 24
    self.good_night = 0
    self.good_night_str = [
      '很晚了，去睡覺，晚安~'
      "超過 " + str(self.sleep_time) + " 點了, 快去睡覺~",
      "再不睡妳明天又要賴床爬不起來了",
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

#如果要插入連結(尚未測試)
embed = discord.Embed()

#調用event函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
  print('目前登入身份：', client.user)

@client.event
#當有訊息時
async def on_message(message):
  # print(dir(message))
  print(message.author, message.content, message.created_at)
  # print(dir(message.created_at))

  #排除自己的訊息，避免陷入無限循環
  if message.author == client.user:
    return

  # 20230615 有更新 id 要注意
  if "Vicky" in str(message.author) :
  # if "zacheen" in str(message.author):
    if '不愛你' in message.content:
      await message.channel.send('但是我還很愛你')
    elif '愛你' in message.content:
      await message.channel.send('請當面告訴帥寶貝')
    if '分手' in message.content:
      await message.channel.send('別想了! 反正我是不會答應的!')

    # 取得當下時間 #####################################
    # <方法1 看觸發的時間>
    # from datetime import datetime,timezone,timedelta
    # dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    # dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區: +8 的時區
    # now_hour = dt2.hour
    # <方法2 看發文的時間>
    now_hour = message.created_at.hour
    ###################################################
    now_hour += 8 # 轉成台灣時區
    if now_hour > 24 :
      now_hour -= 24
    if mem.good_night < len(mem.good_night_str) and (now_hour >= mem.sleep_time
                                                     or now_hour <= 4):
      await message.channel.send(mem.good_night_str[mem.good_night])
      mem.good_night += 1

  # 提醒事項
  if Remind.add_rem in message.content:
    to_add_mess = message.content.replace(Remind.add_rem,"").strip()
    with open(os.getenv(r'REMIND_PATH'), "a") as fw : # append
      fw.write(to_add_mess+"\n")
      await message.channel.send("成功紀錄 : "+to_add_mess)
  elif Remind.remove_rem in message.content:
    try :
      to_remove_mess = int(message.content.replace(Remind.remove_rem,"").strip())
      Remind.del_indx(to_remove_mess)
      await message.channel.send("刪除結果 :\n" + Remind.get_all_rem())
    except :
      await message.channel.send("移除失敗")
  elif Remind.list_rem in message.content:
    await message.channel.send(Remind.get_all_rem())
  
  if "help" == message.content :
    await message.channel.send(Remind.get_help())


#新成員加入時觸發(尚未驗證)
@client.event
async def on_member_join(member):
  pass
  # 目前不會用到，因為看到所以先記錄一下
  # guild = client.get_guild(GUILD_ID)
    # for channel in guild.channels:
    #     if channel.name == '一般':#<<記得改"一般"
    #         await channel.send(f"<@{member.id}> 你好呀:sunglasses:  請輸入你的遊戲ID，管理員看到就會把你加進公會~")

import keep_alive
keep_alive.keep_alive()
client.run(TOKEN)
