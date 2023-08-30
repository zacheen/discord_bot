import json
from glob import glob
import os
from discord import app_commands, Interaction

# 創建 remind 的 json 存放的資料夾 
try :
    os.mkdir(os.getenv(r'REMIND_DIR'))
except FileExistsError :
    pass

from discord.ext import commands
class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    add_rem = ['rem-add','新增提醒事項']
    remove_rem = ['rem-remove','移除提醒事項']
    list_rem = ['rem-list','列出此頻道提醒事項']
    list_all_rem = ['rem-list_all','列出全部提醒事項']
    all_command = [add_rem, remove_rem, list_rem, list_all_rem,]
    find_all_file_pattern = os.getenv(r'REMIND_PATH').replace(".txt", "*.txt")

    def get_help():
        help_str = "目前共有"+str(len(Remind.all_command))+"種指令\n    "
        help_str += "\n    ".join("/"+each_item[0]+" : "+each_item[1] for each_item in Remind.all_command)
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

    @app_commands.command(name = add_rem[0], description = add_rem[1])
    @app_commands.describe(mess = "提醒事項")
    async def add_remind(self, interaction: Interaction, mess: str):
        try :
            Remind.add_item(interaction.channel, mess)
            await interaction.response.send_message(
                "成功紀錄 : "+mess+"\n"+
                "目前提醒事項 : \n"+ 
                Remind.get_rem(interaction.channel)
                )
        except :
            await interaction.response.send_message("加入失敗")

    @app_commands.command(name = remove_rem[0], description = remove_rem[1])
    @app_commands.describe(remove_idx = "移除第幾個")
    async def remove_remind(self, interaction: Interaction, remove_idx: int):
        try :
            Remind.del_indx(interaction.channel, remove_idx)
            await interaction.response.send_message("刪除結果 :\n" + Remind.get_rem(interaction.channel))
        except :
            await interaction.response.send_message("移除失敗")
    
    @app_commands.command(name = list_rem[0], description = list_rem[1])
    async def list_remind(self, interaction: Interaction):
        await interaction.response.send_message(Remind.get_rem(interaction.channel))
    
    @app_commands.command(name = list_all_rem[0], description = list_all_rem[1])
    async def list_all_remind(self, interaction: Interaction):
        await interaction.response.send_message(Remind.get_all_rem())
    
    @app_commands.command(name = "help_remind", description = "列出提醒事項的所有指令")
    async def help_remind(self, interaction: Interaction):
        await interaction.response.send_message(Remind.get_help())

    @commands.Cog.listener()
    async def on_message(self, message):
        #排除自己的訊息，避免陷入無限循環
        if message.author == self.bot.user:
            return
        if "rem" in message.content and "help" in message.content:
            await message.reply(Remind.get_help())
        

async def setup(bot: commands.Bot):
    print("Remind command loaded")
    await bot.add_cog(Remind(bot))
