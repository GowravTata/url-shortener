#!/bin/bash

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

set -ex

export DEBIAN_FRONTEND=noninteractive

# Update packages
sudo apt update

# Install required tools
sudo apt install -y git curl unzip

# Install AWS CLI if not present
if ! command -v aws >/dev/null 2>&1; then
    echo "Installing AWS CLI..."

    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
        -o awscliv2.zip

    unzip -q awscliv2.zip

    ./aws/install

    rm -rf aws awscliv2.zip
else
    echo "AWS CLI already installed"
    aws --version
fi

# Verify IAM role access
aws sts get-caller-identity

# Configure CodeCommit
git config --system credential.helper '!aws codecommit credential-helper $@'
git config --system credential.UseHttpPath true

# Repository location
REPO_DIR="/home/ubuntu/URL-Shortener"

# Remove existing repository if present
rm -rf "$REPO_DIR"

# Clone repository
git clone \
    https://git-codecommit.ap-south-2.amazonaws.com/v1/repos/URL-Shortener \
    "$REPO_DIR"

# Give ownership to ubuntu user
chown -R ubuntu:ubuntu "$REPO_DIR"

# Fetch and checkout branch as ubuntu user
sudo -u ubuntu git -C "$REPO_DIR" fetch --all
sudo -u ubuntu git -C "$REPO_DIR" checkout feature/local-code-branch

echo "=================================================="
echo "Repository contents"
echo "=================================================="
ls -la "$REPO_DIR"

echo "=================================================="
echo "Searching for compose files"
echo "=================================================="
find "$REPO_DIR" -maxdepth 3 \( \
    -name "docker-compose.yml" -o \
    -name "docker-compose.yaml" -o \
    -name "compose.yml" -o \
    -name "compose.yaml" \
\)

echo "=================================================="
echo "Current branch"
echo "=================================================="
sudo -u ubuntu git -C "$REPO_DIR" branch

# Make run script executable
chmod +x "$REPO_DIR/run.sh"

echo "=================================================="
echo "Executing run.sh"
echo "=================================================="

# Run from repository root directory
sudo -u ubuntu bash -c "
    cd '$REPO_DIR'

    echo 'Current Directory:'
    pwd

    echo 'Directory Contents:'
    ls -la

    echo 'Compose Validation:'
    docker compose config

    ./run.sh
"

echo "=================================================="
echo "User Data completed successfully"
echo "=================================================="

echo "Run cd URL/Shortener "
echo "sudo docker compose --profile tools up -d"
