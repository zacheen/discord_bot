import os
from dotenv import load_dotenv
# 讀取設定
load_dotenv(r"./settings/.env")
TOKEN = os.getenv(r'TOKEN')

import os, asyncio, discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "$", intents = intents)

# 當機器人完成啟動時
@bot.event
async def on_ready():
    print("in on_ready")
    # await bot.load_extension("cogs.slash")
    # await bot.load_extension("no_this_file")
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")
    print("on_ready finish")
    

# 載入指令程式檔案
@bot.command()
async def load(ctx: commands.Context, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.")

# 卸載指令檔案
@bot.command()
async def unload(ctx: commands.Context, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"UnLoaded {extension} done.")

# 重新載入程式檔案
@bot.command()
async def reload(ctx: commands.Context, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")

# 一開始bot開機需載入全部程式檔案
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"load extention <cogs.{filename[:-3]}>")
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        # await bot.load_extension("cogs.slash")
        await bot.start(TOKEN)

# 確定執行此py檔才會執行
if __name__ == "__main__":
    asyncio.run(main())
