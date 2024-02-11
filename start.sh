#!/bin/bash

# Update project
git pull

# Check if the virtual environment exists
if [ -d "venv" ]
then
    echo "Virtual environment exists. Starting..."
    source venv/bin/activate
else
    echo "Virtual environment does not exist. Creating..."
    python -m venv venv
    source venv/bin/activate
    # You can add any additional setup steps here if needed
fi

# install all requirements
pip install -r requirements.txt

# start the process
nohup python3 leaderboard_bot.py &
