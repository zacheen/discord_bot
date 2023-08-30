def get_help(command_class):
    print("__name__",command_class.__name__)
    help_str = f"目前 {command_class.__name__} 共有{str(len(command_class.com_name))}種指令\n    "
    help_str +=  "\n    ".join(
        f"/{each_com[0]} : {each_com[1]}" \
            for each_com in command_class.com_name.values())
    return help_str

