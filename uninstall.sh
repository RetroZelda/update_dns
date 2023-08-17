#!/bin/sh
systemctl disable on-network-reconnect.service
rm /etc/systemd/system/on-network-reconnect.service
systemctl daemon-reload
