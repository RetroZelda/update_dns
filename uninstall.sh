#!/bin/sh
systemctl disable on-network-reconnect.service
systemctl disable on-network-reconnect.timer
rm /etc/systemd/system/on-network-reconnect.service
rm /etc/systemd/system/on-network-reconnect.timer
systemctl daemon-reload
