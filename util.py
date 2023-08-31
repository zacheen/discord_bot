def get_help(command_class):
    help_str = f"目前 {command_class.__name__} 共有{str(len(command_class.com_name))}種指令\n    "
    help_str +=  "\n    ".join(
        f"/{each_com[0]} : {each_com[1]}" \
            for each_com in command_class.com_name.values())
    return help_str

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
# google auth 
def get_drive_auth() :
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"./settings/stock-key.json", scope)
    DRIVE = build('drive', 'v3', credentials=creds)
    return DRIVE





