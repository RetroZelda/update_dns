#!/bin/sh
cp ./on-network-reconnect.service /etc/systemd/system/on-network-reconnect.service
chown root:root /etc/systemd/system/on-network-reconnect.service
systemctl daemon-reload
systemctl enable on-network-reconnect.service
