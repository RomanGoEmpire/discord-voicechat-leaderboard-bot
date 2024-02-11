#!/bin/bash

# Find the process ID (PID) of roles_bot.py
PID=$(pgrep -f leaderboard_bot.py)

# Kill the process
if [ -n "$PID" ]; then
  kill $PID
  echo "Process roles_bot.py (PID: $PID) has been killed."
else
  echo "Process roles_bot.py is not running."
fi
