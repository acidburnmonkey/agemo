#!/bin/bash

##
## https://github.com/acidburnmonkey/agemo
##




mkdir -p "$HOME/.local/share/agemo"
cp  -r assets/ agemo.json thumnailer.py HyprParser.py agemo.py  "$HOME/.local/share/agemo"

sed -i "s|{}|${HOME}|g" agemo.desktop
cp agemo.desktop "$HOME/.local/share/applications/"

chmod +x "$HOME/.local/share/agemo/agemo.py"

pip install -r requirements.txt

echo 'Done ,agemo Installed on ~/.local/share/'
