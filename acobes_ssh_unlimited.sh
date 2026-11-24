#!/bin/bash
while true; do
    ssh -tt -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -R 80:127.0.0.1:8000 nokey@localhost.run > ssh_tunnel.log 2>&1
    sleep 4
done
