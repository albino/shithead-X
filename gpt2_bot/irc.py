import ssl
import socket
import sys

class IRCBot:

    def __init__(self, server, port, password, nick, username, realname, channels, ignore_list, command_char, debug):
        self.server = server
        self.port = port
        self.password = password
        self.nick = nick
        self.username = username
        self.realname = realname
        self.channels = channels
        self.ignore_list = ignore_list
        self.command_char = command_char
        self.debug = debug

        self.ready = False
        self.init_done = False

        self.command_handlers = {}

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
                for chan in self.channels:
                    self.__send_line("JOIN :"+chan)

                self.init_done = True
    
    def __send_line(self, line):
        self.__debug("<<<"+line)
        self.socket.send(bytes(line+"\r\n", "UTF-8"))

    def __irc_init(self):
        self.__debug("Introducing ourselves...")
        self.__send_line("USER "+self.username+" 0 * "+self.username)
        self.__send_line("NICK "+self.nick)
        if self.password:
            self.__send_line("PASS "+self.password)

    def __process_line(self, line):
        if line.startswith("PING "):
            self.__send_line("PONG "+line[5:])

        parts = line.split()
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
        if sender in self.ignore_list:
            return

        self.__debug("Heard "+msg+" from "+sender+" in "+chan)

        if msg.startswith(self.command_char):
            parts = msg.split()
            command = parts[0][1:]
            ret = self.command_handlers[command](parts[1:], sender)
            if ret:
                self.__say(ret, chan)

    def __say(self, msg, chan):
        self.__send_line("PRIVMSG "+chan+" :"+msg)

    def register_command(self, name, func):
        self.command_handlers[name] = func
        self.__log("Registered command "+name)
