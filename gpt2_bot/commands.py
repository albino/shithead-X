def ping_command(args, sender):
    if args:
        return sender + ": " + " ".join(args)
    else:
        return sender + ": Pong!"
