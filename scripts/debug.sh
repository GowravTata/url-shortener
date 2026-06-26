echo "==================== BASIC INFO ===================="
date
whoami
id
pwd
echo "HOME=$HOME"
hostname
uname -a

echo
echo "==================== CLOUD INIT STATUS ===================="
sudo cloud-init status --long

echo
echo "==================== USER DATA RECEIVED ===================="
sudo cat /var/lib/cloud/instance/user-data.txt

echo
echo "==================== SCRIPT EXECUTED ===================="
sudo cat /var/lib/cloud/instance/scripts/part-001

echo
echo "==================== CLOUD INIT OUTPUT LOG ===================="
sudo tail -300 /var/log/cloud-init-output.log

echo
echo "==================== CLOUD INIT JOURNAL ===================="
sudo journalctl -u cloud-init -u cloud-final -n 300 --no-pager

echo
echo "==================== USER DATA CUSTOM LOG ===================="
sudo cat /var/log/user-data.log 2>/dev/null || echo "user-data.log not found"

echo
echo "==================== AWS CLI ===================="
which aws
aws --version

echo
echo "==================== IAM ROLE TEST ===================="
aws sts get-caller-identity

echo
echo "==================== GIT ===================="
which git
git --version

echo
echo "==================== GIT CONFIG ===================="
git config --system --list

echo
echo "==================== URL SHORTENER LOCATION ===================="
sudo find / -type d -name "URL-Shortener" 2>/dev/null

echo
echo "==================== HOME UBUNTU ===================="
ls -la /home/ubuntu

echo
echo "==================== ROOT HOME ===================="
sudo ls -la /root

echo
echo "==================== REPOSITORY CONTENTS ===================="
ls -la /home/ubuntu/URL-Shortener 2>/dev/null || echo "Repo not found in /home/ubuntu"

echo
echo "==================== BRANCH ===================="
cd /home/ubuntu/URL-Shortener 2>/dev/null && git branch && git status

echo
echo "==================== RUN.SH ===================="
cd /home/ubuntu/URL-Shortener 2>/dev/null && ls -l run.sh

echo
echo "==================== DOCKER ===================="
which docker
docker --version

echo
echo "==================== DOCKER COMPOSE ===================="
docker compose version

echo
echo "==================== DOCKER SERVICE ===================="
sudo systemctl status docker --no-pager

echo
echo "==================== DOCKER CONTAINERS ===================="
docker ps -a

echo
echo "==================== DOCKER IMAGES ===================="
docker images

echo
echo "==================== DOCKER COMPOSE LOGS ===================="
cd /home/ubuntu/URL-Shortener 2>/dev/null && docker compose logs --tail=100

echo
echo "==================== OPEN PORTS ===================="
sudo ss -tulpn

echo
echo "==================== MEMORY ===================="
free -h

echo
echo "==================== DISK ===================="
df -h

echo
echo "==================== PROCESS LIST ===================="
ps aux --sort=-%mem | head -20

echo
echo "==================== KAFKA TOPICS ===================="
docker exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null || echo "Kafka container not available"

echo
echo "==================== POSTGRES CONTAINERS ===================="
docker ps -a | grep postgres || true

echo
echo "==================== FINAL CLOUD INIT STATUS ===================="
sudo cloud-init status --long