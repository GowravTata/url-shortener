# Add Docker's official GPG key
sudo apt update
sudo apt install -y ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc


echo "=================================================="
echo "Add Docker repository"
echo "=================================================="
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

echo "=================================================="
echo "Refresh package cache"
echo "=================================================="

sudo apt update


echo "=================================================="
echo "Install Docker"
echo "=================================================="

sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

echo "=================================================="
echo "Enable and start Docker"
echo "=================================================="

sudo systemctl enable docker
sudo systemctl start docker

echo "=================================================="
echo " Verify installation"
echo "=================================================="

sudo docker --version
sudo docker compose version

echo "=================================================="
echo "Current Branch"
echo "=================================================="

git branch

echo "=================================================="
echo "Compose Validation"
echo "=================================================="

docker compose config

echo "Validating Docker Compose..."
sudo docker compose config

echo "Pulling latest images..."
sudo docker compose pull

echo "Starting containers..."
sudo docker compose up -d


until curl -fs http://localhost:8000/health; do
    sleep 2
done

docker compose exec api python -m scripts.seed_data

echo "=================================================="
echo "Containers"
echo "=================================================="
sudo docker ps

sudo usermod -aG docker ubuntu



echo "=================================================="
echo "Bootstrap completed successfully"
echo "=================================================="
