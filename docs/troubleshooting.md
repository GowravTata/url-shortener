# Docker Permission Denied

sudo usermod -aG docker ubuntu

newgrp docker

---

# PostgreSQL Timeout

Check

docker ps

docker compose logs postgres

---

# Kafka Consumer Not Running

docker compose logs analytics-consumer

---

# Redis Empty

docker compose logs redis

---

# Terraform Apply Failed

terraform state list

terraform output

terraform destroy