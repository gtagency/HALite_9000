#!/bin/bash

if hash python3 2>/dev/null; then
    ./halite -d "30 30" "python3 pybot.py" "java .py"
else
    ./halite -d "30 30" "python MyBot.py" "python RandomBot.py"
fi
