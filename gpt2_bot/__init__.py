import gpt2_bot.irc, gpt2_bot.commands

def assemble_bot(config_path):
    ircbot = gpt2_bot.irc.IRCBot(config_path)

    ircbot.register_command("ping", gpt2_bot.commands.ping_command)
    ircbot.register_command("ignore", gpt2_bot.commands.ignore_command)
    ircbot.register_command("unignore", gpt2_bot.commands.unignore_command)

    return ircbot
