#!/usr/bin/env python3
# An example script to parse an IRC log

# CONFIGURATION

# Possible formats: weechat irssi mirc
log_format = "weechat"
ignore_nicks = ("Kuroki", "manchego", "manchego-ng", "shithead", "shithead-ng", "bigfoot")

# https://github.com/titouanc/pyirclogs
from pyirclogs import parse_file
import sys
import re

if len(sys.argv) == 1:
    print("Usage:", sys.argv[0], "[log file] > [output file]", file=sys.stderr)
    exit()

logs = parse_file(sys.argv[1], parser=log_format)

lines = 0

for msg in logs:
    if msg.nick in ignore_nicks:
        continue
    if not re.compile("[A-Za-z_]").search(msg.nick):
        continue
    lines += 1
    print(msg.text)

if lines == 0:
    print("Warning: no lines processed! Is the log format correct?", file=sys.stderr)
