import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
TOKEN = os.getenv(r'TOKEN')

bot = commands.Bot(command_prefix = "$", intents=discord.Intents.all())
# bot.remove_command('help')

@bot.event
async def on_ready():
    print('on_ready')
    # await bot.change_presence(activity=discord.Game(name='!help'))

# command 裡面的參數 
    # name="ping", description = "description" 目前也沒看到有顯示
    # aliases=['other_name'] 指令別名
@bot.command(name="ping", description = "description", aliases=['p'])
async def ping(ctx, extension = "1"):
    await ctx.send("Pong" * int(extension))

bot.run(TOKEN)
