from aitextgen import aitextgen
import sys
import random
import functools
import re

def __log(msg):
    print("[GPT-2] "+msg, file=sys.stderr)

def init(ircbot):

    config = ircbot.config

    __log("Loading model...")
    ai = aitextgen(model=config["GPT-2"]["model"], config=config["GPT-2"]["config"])
    __log("Quantizing model...")
    ai.quantize()
    __log("Done.")

    history = []

    def handler(bot, msg, sender):
        # Handler for when a message is received
        history.append(msg)

        if len(history) > int(config["GPT-2"]["histlen"]):
            del history[0]

        if random.randrange(0, 100) < bot.data["chattiness"]:
            # Time to shitpost

            num_lines = random.choices(
                [1, 2, 3, 4],
                map(lambda x: int(x), config["GPT-2"]["random_weights"].split())
            )[0]

            hist_length = len( functools.reduce(
                lambda a, b: a + b,
                map(lambda x: x.split(), history)
            ))
            generate_length = hist_length + ( num_lines * int(config["GPT-2"]["linelen"]) )

            generated = ai.generate_one(
                prompt = "\n".join(history)+"\n",
                max_length = generate_length,
                temperature = bot.data["temp"],
            )

            lines = generated.split("\n")[len(history):]
            lines = lines[ :(num_lines) ]

            if config["General"]["debug"] == "yes":
                # Print some nice debug information to see what's happening with text generation
                print("\n[GPT-2 DEBUG] max_length = "+str(generate_length)+"; generated text:\n\n"+generated+"\n")

            def transform_line(line):
                # Quick hack to avoid highlighting people unnecessarily - could be improved if
                # the bot continues to be problematic
                if re.compile('[a-zA-Z0-9_]+[:,]').match(line) and config["GPT-2"]["block_highlights"] == "yes":
                    line = line[0]+"."+line[1:]

                # Greentext
                if line.startswith(">") and config["GPT-2"]["greentext"] == "yes":
                    line = "\x0303"+line

                return line

            lines = map(transform_line, lines)

            return "\n".join(lines)

    ircbot.register_privmsg_handler(handler)
