# coding:utf-8

# python version 3.10 (python 3.7 無法安裝 discord 2.3.0 版)
# pip install -U discord.py
# pip install -U python-dotenv
# pip install apscheduler
# pip install Flask
# pip install pytz

import json
from glob import glob
import os
# os.system("")

from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
MY_DISCORD_ID = os.getenv(r'MY_DISCORD_ID')
print("MY_DISCORD_ID :", MY_DISCORD_ID)

# testing settings
is_testing = os.getenv(r'TESTING') != None
print("is_testing :",is_testing)

import discord
import time
import datetime as datetimeLib
from datetime import datetime
import pytz

#關鍵字
try :
  os.mkdir(os.getenv(r'REMIND_DIR'))
except FileExistsError :
  pass
class Remind():
  add_rem = '加入提醒事項:'
  remove_rem = '刪除提醒事項:'
  list_rem = '列出提醒事項'
  list_all_rem = '列出全部提醒事項'
  all_command = [add_rem, remove_rem, list_rem, list_all_rem,]
  find_all_file_pattern = os.getenv(r'REMIND_PATH').replace(".txt", "*.txt")

  def get_help():
    help_str = "目前共有"+str(len(Remind.all_command))+"種指令\n    "
    help_str += "\n    ".join(Remind.all_command)
    return help_str

  chan_name_key = "channel_name"
  remind_list_key = "remind_list"

  def read_info(channel) : 
    remind_path = os.getenv(r'REMIND_PATH').replace(".txt", str(channel.id)+".txt")
    with open(remind_path, encoding='UTF-8') as fr:
      info = json.load(fr)
      return info
    raise Exception

  def write_info(channel, info) :
    remind_path = os.getenv(r'REMIND_PATH').replace(".txt", str(channel.id)+".txt")
    with open(remind_path, "w") as fw :
      json.dump(info, fw, indent = 4)
      return
    raise Exception

  def get_all_rem() :
    full_remind = ""
    indx = 1
    for each_file in glob(Remind.find_all_file_pattern) :
      try :
        with open(each_file, encoding='UTF-8') as fr:
          info = json.load(fr)
          for each_remind in info[Remind.remind_list_key]:
            full_remind += str(indx)+". "+each_remind + \
              " , 位於 : "+ info[Remind.chan_name_key] +"\n"
            indx += 1
      except FileNotFoundError :
        pass
    if full_remind == "" :
      full_remind = "沒有剩餘提醒事項"
    return full_remind

  def get_rem(channel) :
    full_remind = ""
    try :
      info = Remind.read_info(channel)
      for indx, each_remind in enumerate(info[Remind.remind_list_key], 1) :
        full_remind += str(indx)+". " + each_remind + "\n"
    except FileNotFoundError :
      full_remind = "之前尚未建立過提醒事項"
    if full_remind == "" :
      full_remind = "沒有剩餘提醒事項"
    return full_remind

  def add_item(channel, item) :
    remind_path = os.getenv(r'REMIND_PATH').replace(".txt", str(channel.id)+".txt")
    if os.path.isfile(remind_path) : 
      info = Remind.read_info(channel)
    else :
      info = {
        Remind.chan_name_key : channel.name, 
        Remind.remind_list_key : []
      }

    info[Remind.remind_list_key].append(item)
    Remind.write_info(channel, info)

  def del_indx(channel, tar_indx) : # indx start : 1
    info = Remind.read_info(channel)
    del(info[Remind.remind_list_key][tar_indx-1])
    Remind.write_info(channel,info)
    

from discord.ext import commands, tasks
#紀錄狀態
class Memery(commands.Cog):
  reset_time = datetimeLib.time(hour=1, minute=22, tzinfo=datetimeLib.timezone.utc) # 不能用 pytz 的 timezone 會跳 WARNING !!
  def __init__(self):
    self.reset.start()
    pass

  def cog_unload(self):
    print("execute cog_unload !!!!!!!!!!")
    self.reset.cancel()

  # @tasks.loop(seconds=5.0) # 要記得 start 才會開始 loop
  @tasks.loop(time = reset_time)
  async def reset(self):
    print("reset")
    self.sleep_time = 24
    self.skip_day = [5,6]
    self.good_night = 0
    self.good_night_str = [
      '很晚了，去睡覺，晚安~'
      "超過 " + str(self.sleep_time) + " 點了, 快去睡覺~",
      "再不睡妳明天又要賴床爬不起來了",
      '妳給我睡覺喔! 😡'
    ]

    # 交往紀念日
    anniversary = datetime.strptime("2023 03 08 20:00:00 +0800", "%Y %m %d %H:%M:%S %z")  # 這個日期格式不要加上時區
    anniversary_days = (datetime.now(pytz.timezone("Asia/Taipei")) - anniversary).days + 1
    print(anniversary_days,"days")

    await send_message()
    print("reset finish")

async def send_message(message = "test", channel_id = 1122539631443972246):
  to_send_chan = client.get_channel(channel_id)
  await to_send_chan.send(message)

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
  global mem
  mem = Memery()
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
  if is_testing or MY_DISCORD_ID not in str(message.author) :
  # if "zacheen" in str(message.author):
    if '不愛你' in message.content:
      await message.channel.send('但是我還很愛你')
    elif '愛你' in message.content:
      await message.channel.send('請當面告訴帥寶貝')
    if '分手' in message.content:
      await message.channel.send('別想了! 反正我是不會答應的!')

    baby_time = datetime.now(pytz.timezone("America/Los_Angeles"))
    now_hour = baby_time.hour
    if mem.good_night < len(mem.good_night_str) and \
        (now_hour >= mem.sleep_time or now_hour <= 4) and \
        not (baby_time.weekday() in mem.skip_day) : # 排除日期
      await message.channel.send(mem.good_night_str[mem.good_night])
      mem.good_night += 1

  # 提醒事項
  if Remind.add_rem in message.content:
    try :
      to_add_mess = message.content.replace(Remind.add_rem,"").strip()
      Remind.add_item(message.channel, to_add_mess)
      await message.channel.send("成功紀錄 : "+to_add_mess)
    except :
      await message.channel.send("加入失敗")
  elif Remind.remove_rem in message.content:
    try :
      to_remove_mess = int(message.content.replace(Remind.remove_rem,"").strip())
      Remind.del_indx(message.channel, to_remove_mess)
      await message.channel.send("刪除結果 :\n" + Remind.get_rem(message.channel))
    except :
      await message.channel.send("移除失敗")
  elif Remind.list_rem in message.content:
    await message.channel.send(Remind.get_rem(message.channel))
  elif Remind.list_all_rem in message.content:
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

TOKEN = os.getenv(r'TOKEN')
print("TOKEN :", TOKEN)
# import keep_alive
# keep_alive.keep_alive()
client.run(TOKEN)
print("client offline")
