#!/bin/bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y docker.io docker-compose-v2 ca-certificates curl
systemctl enable --now docker
usermod -aG docker ubuntu

install -d -m 0755 -o ubuntu -g ubuntu /opt/practicarta
install -d -m 0700 -o ubuntu -g ubuntu /opt/practicarta-backups

if ! swapon --show | grep -q /swapfile; then
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
