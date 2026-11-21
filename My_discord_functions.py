import os
DEFAULT_CHANNEL = int(os.getenv(r'DEFAULT_CHANNEL'))
# DRIVE_PIC_URL = os.getenv(r'GOOGLE_DRIVE_PIC_URL')
is_testing = os.getenv(r'TESTING') != None

import requests
from bs4 import BeautifulSoup

import random
from datetime import datetime
import pytz

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from util import *

# drive download
import io
from googleapiclient.http import MediaIoBaseDownload

def set_bot(pass_bot):
    global bot
    bot = pass_bot

async def send_message(message = "test", channel_id = DEFAULT_CHANNEL):
    to_send_chan = bot.get_channel(channel_id)
    await to_send_chan.send(message)

async def send_embed(url, message, channel_id = DEFAULT_CHANNEL):
    to_send_chan = bot.get_channel(channel_id)
    em = discord.Embed(description = message, url = url)
    # em.set_image(url = url)
    # em.set_thumbnail(url = url)
    if message == "":
        em.description = "Embed"
    await to_send_chan.send(embed = em)

async def send_file(file_path, channel_id = DEFAULT_CHANNEL):
    if type(channel_id) == int :
        to_send_chan = bot.get_channel(channel_id)
    else :
        to_send_chan = channel_id
    filename = file_path.split("\\")[-1]
    dis_file = discord.File(file_path, filename=filename)
    await to_send_chan.send(file = dis_file)

# 隨機一張 google drive 裡面的圖片 ###################################
class Random_pic(commands.Cog):
    com_name = {
        # "to" : ["today_pic", "今日圖片"],
        "ano" : ["another_pic", "再隨機一張圖片"],
    }
    temp_pic_path = "./temp_pic.jpeg"
    
    def __init__(self):
        self.DRIVE = get_drive_auth()

    ## new method ##########################################################
    ## 透過 google auth 跟 API，直接下載圖片，再上傳到discord
    def get_random_pic_id(self):
        results = self.DRIVE.files().list(
            q = "mimeType='image/jpeg'",    # 搜尋條件
            fields="files(id, name)" #限制回傳的欄位
        ).execute()

        all_pic = results.get('files', [])
        return random.choice(all_pic)["id"]
    
    def download_from_drive(self, file_id):
        request = self.DRIVE.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        download_byte = file.getvalue()
        
        with open(Random_pic.temp_pic_path, "wb") as fw : 
            fw.write(download_byte)

    async def daily_drive_pic(self):
        self.download_from_drive(self.get_random_pic_id())
        await send_file(Random_pic.temp_pic_path)
    
    @app_commands.command(name = com_name["ano"][0], description = com_name["ano"][1])
    async def another_pic(self, interaction):
        to_send_chan = interaction.channel
        await interaction.response.send_message("OK~")
        self.download_from_drive(self.get_random_pic_id())
        await send_file(Random_pic.temp_pic_path, to_send_chan)

    ## old method ##########################################################
    ## 把資料夾的權限調成"知道連結的任何人 可檢視"，再產出連結導到預覽畫面
    # def reset_pic(self):
    #     self.today_pic_path = ""
    
    # @app_commands.command(name = com_name["to"][0], description = com_name["to"][1])
    # async def today_pic(self, interaction: Interaction):
    #     await self.send_pic(interaction, False)

    # @app_commands.command(name = com_name["ano"][0], description = com_name["ano"][1])
    # async def another_pic(self, interaction: Interaction):
    #     await self.send_pic(interaction, True)
    
    # async def send_pic(self, interaction, force_new = False):
    #     to_send_chan = interaction.channel
    #     await interaction.response.send_message("OK~")
    #     if force_new or self.today_pic_path == "" :
    #         self.today_pic_path = "https://drive.google.com/uc?id="+Random_pic.get_random_pic_id()
    #     url = Random_pic.get_redirect_url(self.today_pic_path)
    #     # await interaction.response.send_message(embed=em) # 運作時間太長
    #     await to_send_chan.send(url)

    # async def everyday_send_drive_image(self, channel_id = DEFAULT_CHANNEL):
    #     self.today_pic_path = "https://drive.google.com/uc?id=" + Random_pic.get_random_pic_id()
    #     url = Random_pic.get_redirect_url(self.today_pic_path)
    #     to_send_chan = bot.get_channel(channel_id)
    #     await to_send_chan.send(url)

    # def get_random_pic_id():
    #     all_pic_id = []
    #     web = requests.get(DRIVE_PIC_URL)       # 取得網頁內容
    #     web.encoding = 'UTF-8'
    #     soup = BeautifulSoup(web.text, "html.parser")  # 轉換成標籤樹
    #     for all_div in soup.find_all('div'):    # 找出全部的 div
    #         data_id = all_div.get('data-id')    # 取出某個欄位的名稱 (若沒找到則為 None)
    #         if data_id != None :
    #             all_pic_id.append(data_id)
    #     return random.choice(all_pic_id)

    # # 取得 網頁跳轉 之後的網址
    # def get_redirect_url(url):
    #     web = requests.get(url)     # 取得網頁內容
    #     return web.url

# 每天想說的話 ##################################################
normal_congrat = [
                  "今天是第 @@ 天交往，寶貝我愛妳~🥰",
                  "今天是第 @@ 天交往，寶貝我愛妳~💕",
                  "今天是第 @@ 天交往，寶貝相信自己! 不相信自己就是不相信我的眼光",
                  "今天是第 @@ 天交往，我知道妳很想我，但還是要乖乖準時去睡覺喔",
                  "今天是第 @@ 天交往，再撐一下，我一定會過去找妳的!",
                  "今天是第 @@ 天交往，誰說一定要是特別的天數才能慶祝~",
                  "今天是第 @@ 天交往，快去跟寶貝討親親獎勵",
                  "今天是第 @@ 天交往，如果從親嘴那天開始計算還更多天喔😏",
                  "今天是第 @@ 天交往，好想要親妳喔~姆啊😙",
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

ANNIVERSARY = os.getenv(r'ANNIVERSARY')
def get_anniversary_days():
    anniversary = datetime.strptime(ANNIVERSARY, "%Y %m %d %H:%M:%S %z")
    anniversary_days = (datetime.now(pytz.timezone("Asia/Taipei")) - anniversary).days + 1
    return anniversary_days

# go to sleep! ##################################################
MY_DISCORD_ID = os.getenv(r'MY_DISCORD_ID')
print("MY_DISCORD_ID :", MY_DISCORD_ID)

from discord.ext import commands
class Go_to_sleep(commands.Cog):
    def __init__(self, bot):
        self.good_night = 0
        self.sleep_time = 24
        self.skip_day = [5,6]
        self.good_night_str = [
            '很晚了，去睡覺，晚安~'
            "超過 " + str(self.sleep_time) + " 點了, 快去睡覺~",
            "再不睡妳明天又要賴床爬不起來了",
            '妳給我睡覺喔! 😡'
        ]
        self.bot = bot

    def tell_go_to_sleep(self):
        if self.chech_sleep_time() \
              and self.good_night < len(self.good_night_str):
            ret_str = self.good_night_str[self.good_night]
            self.good_night += 1
            return ret_str
        return None
    
    def chech_sleep_time(self):
        baby_time = datetime.now(pytz.timezone("America/Los_Angeles"))
        now_hour = baby_time.hour
        if (now_hour >= self.sleep_time or now_hour <= 4) and \
            not (baby_time.weekday() in self.skip_day): # 排除日期
                return True
        return False
    
    def reset_sleep(self):
        self.good_night = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        #排除自己的訊息，避免陷入無限循環
        if message.author == self.bot.user:
            return
        # 不包含指令
        # print(message.author, message.content, message.created_at)
        # 20230615 有更新 id 要注意
        if is_testing or MY_DISCORD_ID not in str(message.author):
        # if "zacheen" in str(message.author):
            if '不愛你' in message.content:
                await message.channel.send('但是我還很愛你')
            elif '愛你' in message.content:
                await message.reply('請當面告訴帥寶貝')
            if '分手' in message.content:
                await message.reply('別想了! 反正我是不會答應的!')

            ret_str = self.tell_go_to_sleep()
            if ret_str != None :
                await message.channel.send(ret_str)





