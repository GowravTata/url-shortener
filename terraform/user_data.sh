#!/bin/bash

exec > >(tee /var/log/user-data.log)
exec 2>&1

set -ex

export DEBIAN_FRONTEND=noninteractive

apt update
apt install -y git

REPO_NAME="${repo_name}"
GITHUB_USERNAME="${github_username}"

REPO_DIR="/home/ubuntu/${repo_name}"

rm -rf "$REPO_DIR"

git clone \
    "https://github.com/$${GITHUB_USERNAME}/$${REPO_NAME}.git" \
    "$REPO_DIR"

chown -R ubuntu:ubuntu "$REPO_DIR"

chmod +x "$REPO_DIR/ec2_bootstrap.sh"

sudo -u ubuntu bash -c "
    cd '$REPO_DIR'
    ./ec2_bootstrap.sh
"