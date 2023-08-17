#!/bin/sh

# Specify the target user and script name
TARGET_USER="retrozelda"
SCRIPT_DIR="/home/retrozelda/update_dns"
DATE=$(date +'%m_%d_%Y-%H_%M_%S')

# Switch to the target user and execute the script from its directory
su - $TARGET_USER -c "cd $SCRIPT_DIR && python3 ./update_dns.py | tee latest.log ./logs/$DATE.log"
