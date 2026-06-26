#!/bin/bash

exec > >(tee /var/log/ec2-bootstrap.log)
exec 2>&1

set -ex

REPO_DIR="$(pwd)"

echo "=================================================="
echo "Current Directory"
echo "=================================================="
pwd

echo "=================================================="
echo "Repository Contents"
echo "=================================================="
ls -la

echo "=================================================="
echo "Installing Docker"
echo "=================================================="

curl -fsSL https://get.docker.com | sh

sudo systemctl enable docker
sudo systemctl start docker

echo "=================================================="
echo "Docker Version"
echo "=================================================="

docker --version
docker compose version

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
echo "Current Branch"
echo "=================================================="

git branch

echo "=================================================="
echo "Making run.sh executable"
echo "=================================================="

chmod +x "$REPO_DIR/run.sh"

echo "=================================================="
echo "Compose Validation"
echo "=================================================="

docker compose config

echo "=================================================="
echo "Executing run.sh"
echo "=================================================="

./run.sh

echo "=================================================="
echo "Bootstrap completed successfully"
echo "=================================================="