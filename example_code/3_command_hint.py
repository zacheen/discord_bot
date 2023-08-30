import os
from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
TOKEN = os.getenv(r'TOKEN')

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from discord.app_commands import Choice
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "/", intents = intents)

@bot.event
async def on_ready():
    await bot.add_cog(Greetings(bot))
    slash = await bot.tree.sync()  # 一定要執行這行 command 才會同步到 discord
    print(f"目前登入身份 --> {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    # name指令名稱，description指令敘述
    # 指令還不能超時，且不能 response 兩次
        # 解決方法
        # to_send_chan = interaction.channel # 先記錄 channel
        # await to_send_chan.send(message)   # 再用此 channel 發送訊息
    @app_commands.command(name = "hello", description = "Hello, world!")
    async def hello(self, interaction: discord.Interaction):
        # 回覆使用者的訊息
        await interaction.response.send_message("Hello, world!")

    # @app_commands.describe(參數名稱 = 參數敘述)
    # 參數: 資料型態，可以限制使用者輸入的內容
    @app_commands.command(name = "add", description = "計算相加值")
    @app_commands.describe(a = "輸入數字", b = "輸入數字")
    async def add(self, interaction: discord.Interaction, a: int, b: int):
        await interaction.response.send_message(f"Total: {a + b}")

    # 參數: Optional[資料型態]，參數變成可選，可以限制使用者輸入的內容
    @app_commands.command(name = "say", description = "大聲說出來")
    @app_commands.describe(name = "輸入人名", text = "輸入要說的話")
    async def say(self, interaction: discord.Interaction, name: str, text: Optional[str] = None):
        if text == None:
            text = "。。。"
        await interaction.response.send_message(f"{name} 說 「{text}」")

    # @app_commands.choices(參數 = [Choice(name = 顯示名稱, value = 隨意)])
    @app_commands.command(name = "order", description = "點餐機")
    @app_commands.describe(meal = "選擇餐點", size = "選擇份量")
    @app_commands.choices(
        meal = [
            Choice(name = "漢堡", value = "hamburger"),
            Choice(name = "薯條", value = "fries"),
            Choice(name = "雞塊", value = "chicken_nuggets"),
        ],
        size = [
            Choice(name = "大", value = 0),
            Choice(name = "中", value = 1),
            Choice(name = "小", value = 2),
        ]
    )
    async def order(self, interaction: discord.Interaction, meal: Choice[str], size: Choice[int]):
        # 獲取使用指令的使用者名稱
        customer = interaction.user.name
        # 使用者選擇的選項資料，可以使用name或value取值
        meal = meal.value
        size = size.value
        await interaction.response.send_message(f"{customer} 點了 {size} 號 {meal} 餐")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        #排除自己的訊息，避免陷入無限循環
        if message.author == self.bot.user:
            return
        print("you say : "+message.content)

if __name__ == "__main__":
    bot.run(TOKEN)