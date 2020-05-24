import ssl
import socket
import sys

import gpt2_bot.config

class IRCBot:

    def __init__(self, config_file):

        self.ready = False
        self.init_done = False
        self.command_handlers = {}
        self.privmsg_handler = None

        # Important note on config:
        #
        # This class implements two ways of providing stored data:
        #
        # self.config remains constant for the entire runtime of the bot
        # - it should be treated as immutable
        #
        # self.data represents the most up-to-date data store, and is mutable
        # - when modified save_data should be called.

        self.config = gpt2_bot.config.config(config_file)
        self.data = gpt2_bot.config.read_data(self.config["General"]["data_file"])

        self.server = self.config["IRC"]["hostname"]
        self.port = int(self.config["IRC"]["port"])
        self.password = self.config["IRC"]["password"]
        self.nick = self.config["IRC"]["nick"]
        self.username = self.config["IRC"]["username"]
        self.realname = self.config["IRC"]["realname"]
        self.channels = self.config["IRC"]["channels"].split()
        self.command_char = self.config["IRC"]["command_char"]
        self.identify_line = self.config["IRC"]["identify_line"]
        self.debug = self.config["General"]["debug"] == "yes"

    def save_data(self):
        self.__log("Saving data...")
        gpt2_bot.config.save_data(self.config["General"]["data_file"], self.data)

    def __debug(self, msg):
        if self.debug:
            print("[DEBUG]", msg, file=sys.stderr)

    def __log(self, msg):
        print("[IRC]", msg, file=sys.stderr)

    def start(self):
        ctx = ssl.create_default_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.socket = ctx.wrap_socket(sock, server_hostname=self.server)

        self.__log("Connecting to "+self.server+" on port "+str(self.port))
        self.socket.connect((self.server, self.port))
        self.__debug("Socket connected")

        self.__irc_init()

        # Main event loop
        while True:
            # HACK
            lines = self.socket.recv(524288).decode("UTF-8")
            for line in lines.splitlines():
                self.__debug(">>>"+line)
                self.__process_line(line)

            if self.ready and not self.init_done:
                self.__irc_on_ready()
                self.init_done = True
    
    def __send_line(self, line):
        self.__debug("<<<"+line)
        self.socket.send(bytes(line+"\r\n", "UTF-8"))

    def __irc_init(self):
        self.__debug("Introducing ourselves...")
        if self.password:
            self.__send_line("PASS "+self.password)
        self.__send_line("USER "+self.username+" 0 * "+self.realname)
        self.__send_line("NICK "+self.nick)

    def __irc_on_ready(self):
        if self.identify_line:
            self.__send_line(self.identify_line)
        for chan in self.channels:
            self.__send_line("JOIN :"+chan)
        
    def __process_line(self, line):
        if line.startswith("PING "):
            self.__send_line("PONG "+line[5:])

        parts = line.split()
        if len(parts) < 2:
            return

        if parts[1] == "376":
            # Do all networks send 376 when they are ready?
            self.__log("Successfully connected")
            self.ready = True

        if parts[1] == "PRIVMSG":
            chan = parts[2]
            # Ignore messages not in-channel for now
            if chan in self.channels:
                # Hack: we partion on the string " :" because it first appears right before 
                # the message part of the line
                msg = line.partition(" :")[2]
                sender = parts[0][1:].split("!")[0]
                self.__process_privmsg(msg, sender, chan)

    def __process_privmsg(self, msg, sender, chan):
        if sender in self.data["ignore_list"]:
            return

        self.__debug("Heard "+msg+" from "+sender+" in "+chan)

        if msg.startswith(self.command_char):
            parts = msg.split()
            command = parts[0][1:]
            if not command in self.command_handlers:
                # Fail silently
                return
            ret = self.command_handlers[command](self, parts[1:], sender)
            if ret:
                self.__say(ret, chan)

        else:
            ret = self.privmsg_handler(self, msg, sender)
            if ret:
                self.__say(ret, chan)

    def __say(self, msg, chan):
        lines = msg.split("\n")
        for l in lines:
            self.__send_line("PRIVMSG "+chan+" :"+l)

    def register_command(self, name, func):
        self.command_handlers[name] = func
        self.__log("Registered command "+name)

    def register_privmsg_handler(self, func):
        self.privmsg_handler = func
        self.__log("Registered PRIVMSG handler")
