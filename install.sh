#!/bin/sh
cp ./on-network-reconnect.service /etc/systemd/system/on-network-reconnect.service
cp ./on-network-reconnect.timer /etc/systemd/system/on-network-reconnect.timer
chown root:root /etc/systemd/system/on-network-reconnect.service
chown root:root /etc/systemd/system/on-network-reconnect.timer
systemctl daemon-reload
systemctl start on-network-reconnect.timer
systemctl enable on-network-reconnect.timer
