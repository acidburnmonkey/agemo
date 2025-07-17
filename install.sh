#!/bin/bash

##
## https://github.com/acidburnmonkey/agemo
##

mkdir -p "$HOME/.local/share/agemo"
cp  -r assets/ agemo.json *.py style.qss pyproject.toml uv.lock "$HOME/.local/share/agemo"

mkdir -p "$HOME/.local/share/applications/"
sed -i "s|{}|${HOME}|g" agemo.desktop
cp agemo.desktop "$HOME/.local/share/applications/"

chmod +x "$HOME/.local/share/agemo/agemo.py"
echo 'Done ,agemo Installed on ~/.local/share/'

echo 'if you get an error install uv  and run it from terminal: uv run $HOME/.local/share/agemo/agemo.py'
