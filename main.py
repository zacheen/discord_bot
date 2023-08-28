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
import requests
from bs4 import BeautifulSoup
import random
import json
from glob import glob
import os
# os.system("")

from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
MY_DISCORD_ID = os.getenv(r'MY_DISCORD_ID')
print("MY_DISCORD_ID :", MY_DISCORD_ID)
DEFAULT_CHANNEL = int(os.getenv(r'DEFAULT_CHANNEL'))
print("DEFAULT_CHANNEL :", DEFAULT_CHANNEL)
drive_pic_url = os.getenv(r'GOOGLE_DRIVE_PIC_URL')

# testing settings
is_testing = os.getenv(r'TESTING') != None
print("is_testing :",is_testing)

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
    self.sleep_time = 24
    self.skip_day = [5,6]
    self.good_night_str = [
      '很晚了，去睡覺，晚安~'
      "超過 " + str(self.sleep_time) + " 點了, 快去睡覺~",
      "再不睡妳明天又要賴床爬不起來了",
      '妳給我睡覺喔! 😡'
    ]
    self.reset.start()
    pass

  def cog_unload(self):
    print("execute cog_unload !!!!!!!!!!")
    self.reset.cancel()

  # @tasks.loop(seconds=5.0) # 要記得 start 才會開始 loop
  @tasks.loop(time = reset_time)
  async def reset(self):
    print("reset")
    self.good_night = 0

    # 交往紀念日
    anniversary = datetime.strptime("2023 03 08 20:00:00 +0800", "%Y %m %d %H:%M:%S %z")  # 這個日期格式不要加上時區
    anniversary_days = (datetime.now(pytz.timezone("Asia/Taipei")) - anniversary).days + 1
    await send_anniversary(anniversary_days)
    await send_drive_image()
    print("reset finish")

async def send_message(message = "test", channel_id = DEFAULT_CHANNEL):
  to_send_chan = client.get_channel(channel_id)
  await to_send_chan.send(message)

async def send_embed(url, message, channel_id = DEFAULT_CHANNEL):
  to_send_chan = client.get_channel(channel_id)
  em = discord.Embed(description = message, url = url)
  # em.set_image(url = url)
  # em.set_thumbnail(url = url)
  if message == "":
    em.description = "Embed"
  await to_send_chan.send(embed = em)

# 隨機一張 google drive 裡面的圖片
def get_random_pic_id() :
  all_pic_id = []
  web = requests.get(drive_pic_url)                        # 取得網頁內容
  web.encoding = 'UTF-8'
  soup = BeautifulSoup(web.text, "html.parser")  # 轉換成標籤樹
  for all_div in soup.find_all('div'): # 找出全部的 div
    data_id = all_div.get('data-id') # 取出某個欄位的名稱 (若沒找到則為 None)
    if data_id != None :
      all_pic_id.append(data_id)
  return random.choice(all_pic_id)

# 取得 網頁跳轉 之後的網址
def get_redirect_url(url) :
  web = requests.get(url)                        # 取得網頁內容
  return web.url

async def send_drive_image(picture_id = get_random_pic_id(), channel_id = DEFAULT_CHANNEL):
  to_send_chan = client.get_channel(channel_id)
  em = discord.Embed()
  url = "https://drive.google.com/uc?id=" + picture_id
  url = get_redirect_url(url)
  em.set_image(url = url)
  await to_send_chan.send(embed = em)

async def send_file(file_path, channel_id = DEFAULT_CHANNEL):
  to_send_chan = client.get_channel(channel_id)
  filename = file_path.split("\\")[-1]
  dis_file = discord.File(file_path, filename=filename)
  await to_send_chan.send(file = dis_file)

normal_congrat = [
                  "今天是第 @@ 天交往，寶貝我愛妳~🥰",
                  "今天是第 @@ 天交往，寶貝我愛妳~💕",
                  "今天是第 @@ 天交往，寶貝相信自己! 不相信自己就是不相信我的眼光",
                  "今天是第 @@ 天交往，我知道妳很想我，但還是要乖乖準時去睡覺喔",
                  "今天是第 @@ 天交往，再撐一下，我一定會過去找妳的!",
                  "今天是第 @@ 天交往，誰說一定要是特別的天數才能慶祝~",
                  "今天是第 @@ 天交往，快去跟寶貝討親親獎勵",
                  "今天是第 @@ 天交往，如果從親嘴那天開始計算還更多天喔😏",
                  ]
special_congrat = [
                  "今天是第 @@ 天交往了，不跟寶貝聊聊天嗎?",
                  # "今天是第 @@ 天交往了，還不生個小孩嗎?", 
                  #  "今天是第 @@ 天交往了，不去床上壞壞一下嗎😘?", 
                   ]
near_hundred = []
hundred_congrat = ["恭喜! 已經突破 @@ 天了!"]
async def send_anniversary(anniversary_days):
  if (anniversary_days % 100) == 0 :
    await send_message(random.choice(hundred_congrat).replace("@@", str(anniversary_days)))
  elif (random.randint(1,20) == 1):
    await send_message(random.choice(special_congrat).replace("@@", str(anniversary_days)))
  else :
    await send_message(random.choice(normal_congrat).replace("@@", str(anniversary_days)))


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
