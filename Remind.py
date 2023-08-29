import json
from glob import glob
import os

# 創建 remind 的 json 存放的資料夾 
try :
    os.mkdir(os.getenv(r'REMIND_DIR'))
except FileExistsError :
    pass

from discord.ext import commands
class Remind(commands.Cog):
    add_rem = '加入提醒事項'
    remove_rem = '刪除提醒事項'
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

    def read_info(channel): 
        remind_path = os.getenv(r'REMIND_PATH').replace(".txt", str(channel.id)+".txt")
        with open(remind_path, encoding='UTF-8') as fr:
            info = json.load(fr)
            return info

    def write_info(channel, info):
        remind_path = os.getenv(r'REMIND_PATH').replace(".txt", str(channel.id)+".txt")
        with open(remind_path, "w") as fw :
            json.dump(info, fw, indent = 4)
            return

    def get_all_rem():
        full_remind = ""
        indx = 1
        for each_file in glob(Remind.find_all_file_pattern):
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

    def get_rem(channel):
        full_remind = ""
        try :
            info = Remind.read_info(channel)
            for indx, each_remind in enumerate(info[Remind.remind_list_key], 1):
                full_remind += str(indx)+". " + each_remind + "\n"
        except FileNotFoundError :
            full_remind = "之前尚未建立過提醒事項"
        if full_remind == "" :
            full_remind = "沒有剩餘提醒事項"
        return full_remind

    def add_item(channel, item):
        remind_path = os.getenv(r'REMIND_PATH').replace(".txt", str(channel.id)+".txt")
        if os.path.isfile(remind_path): 
            info = Remind.read_info(channel)
        else :
            info = {
                Remind.chan_name_key : channel.name, 
                Remind.remind_list_key : []
            }
        info[Remind.remind_list_key].append(item)
        Remind.write_info(channel, info)

    def del_indx(channel, tar_indx): # indx start : 1
        info = Remind.read_info(channel)
        del(info[Remind.remind_list_key][tar_indx-1])
        Remind.write_info(channel,info)

    @commands.command(aliases=[add_rem])
    async def add_remind(self, ctx, to_add_mess = ""):
        if to_add_mess == "" :
            await ctx.reply("沒有輸入待加入事項")
            return 
        try :
            Remind.add_item(ctx.channel, to_add_mess)
            await ctx.reply("成功紀錄 : "+to_add_mess +"\n目前提醒事項 : \n"+ Remind.get_rem(ctx.channel))
        except :
            await ctx.reply("加入失敗")

    @commands.command(aliases=[remove_rem])
    async def remove_remind(self, ctx, remove_idx = ""):
        if remove_idx == "" :
            await ctx.reply("沒有輸入待加入事項")
            return 
        try :
            to_remove_mess = int(remove_idx)
            Remind.del_indx(ctx.channel, to_remove_mess)
            await ctx.reply("刪除結果 :\n" + Remind.get_rem(ctx.channel))
        except :
            await ctx.reply("移除失敗")
    
    @commands.command(aliases=[list_rem])
    async def list_remind(self, ctx):
        await ctx.reply(Remind.get_rem(ctx.channel))
    
    @commands.command(aliases=[list_all_rem])
    async def list_all_remind(self, ctx):
        await ctx.reply(Remind.get_all_rem())
    
    # @commands.command()
    # async def help(self, ctx, remove_idx = ""):
    #     await ctx.reply(Remind.get_help())