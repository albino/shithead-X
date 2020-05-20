#!/bin/sh
# Quick and dirty filter to remove "bad" lines
sed '/\[YouTube\]/d' |
sed '/\[4[Cc]han\]/d' |
sed '/https\?:\/\//d' |
sed '/^\./d' |
sed '/^s\//d'
