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
