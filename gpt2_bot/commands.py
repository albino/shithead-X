import gpt2_bot.config

check_privilege = lambda bot, sender: sender in bot.config["General"]["admins"].split()
no_permission = lambda sender: sender + ": You don't have permission to do this!"

def ping_command(bot, args, sender):
    if args:
        return sender + ": " + " ".join(args)
    else:
        return sender + ": Pong!"

def ignore_command(bot, args, sender):
    if not check_privilege(bot, sender):
        return no_permission(sender)

    if not args:
        return sender + ": Usage: ignore <user>"

    if args[0] in bot.data["ignore_list"]:
        return sender + ": I'm already ignoring "+args[0]+"!"

    bot.data["ignore_list"].append(args[0])
    bot.save_data()
    
    return "Now ignoring "+args[0]

def unignore_command(bot, args, sender):
    if not check_privilege(bot, sender):
        return no_permission(sender)

    if not args:
        return sender + ": Usage: unignore <user>"

    if not args[0] in bot.data["ignore_list"]:
        return sender + ": I'm not even ignoring "+args[0]+"!"

    bot.data["ignore_list"].remove(args[0])
    bot.save_data()

    return "No longer ignoring "+args[0]

def temp_command(bot, args, sender):
    if not args:
        return "Current temperature: "+str(bot.data["temp"])+"\nRegular temperature range is 0.7 - 1.0 (higher values are crazier)"

    try:
        args[0] = float(args[0])
    except:
        return sender + ": Temperature must be numeric!"

    if not args[0] > 0:
        return sender + ": Temperature must be strictly positive!"

    bot.data["temp"] = args[0]
    bot.save_data()

    return "New temperature is "+str(args[0])

def shitposting_command(bot, args, sender):
    if not args:
        return "Current shitposting level: "+str(bot.data["chattiness"])+"%"

    try:
        args[0] = int(args[0])
    except:
        return sender + ": Chattiness value must be an integer!"

    if args[0] < 0 or args[0] > 100:
        return sender + ": Valid values are 1-100"

    bot.data["chattiness"] = args[0]
    bot.save_data()

    return "OK"
