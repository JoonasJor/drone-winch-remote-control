#!/bin/bash

# Start the pigpio daemon
sudo pigpiod

# Wait a moment to ensure the daemon has started
sleep 1

# Run the main.py script
python /home/vinssipi/vinssi/main.py
