# URL Shortener Service

A scalable URL shortening service built with Python that allows users to register, create shortened URLs, redirect users to original destinations, and track usage analytics.

---

## Features

* User registration and authentication
* URL shortening
* URL redirection
* Click analytics
* Redis caching
* Rate limiting
* URL expiration support
* Asynchronous event processing with Apache Kafka
* RESTful APIs
* OpenAPI/Swagger documentation

---

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* Redis
* Apache Kafka
* Docker
* Docker Compose

---

## Architecture

The application uses **FastAPI** as the core backend service, **PostgreSQL** for persistent storage, **Redis** for caching frequently accessed URLs, and **Apache Kafka** for asynchronous event processing.

When a user accesses a shortened URL, the application immediately redirects the request while publishing a click event to Kafka. A separate analytics consumer processes these events and updates click statistics asynchronously, ensuring that analytics processing does not impact redirect performance.

![System Architecture](images/architecture.png)

### User Flow

```text
Register → Login → Create Short URL
                        |
                        v
                  Share URL
                        |
                        v
                 User Accesses URL
                        |
                        v
                 Redirect Occurs
                        |
                        +---------------------+
                        |                     |
                        v                     v
             Publish Click Event       Return Redirect
                  to Kafka                Response
                        |
                        v
             Analytics Consumer
                        |
                        v
              Analytics Updated
```

---

## Architecture Components

| Component | Responsibility |
|-----------|----------------|
| FastAPI | REST API and business logic |
| PostgreSQL | Persistent storage for users, URLs, and analytics |
| Redis | Cache frequently accessed URLs to reduce database load |
| Apache Kafka | Event streaming for click tracking |
| Analytics Consumer | Consumes Kafka events and updates analytics |
| Docker Compose | Local orchestration of all services |

---

## Prerequisites

* Docker
* Docker Compose

Verify installation:

```bash
docker --version
docker compose version
```

---

## Getting Started

### Clone Repository

```bash
git clone <repository-url>
cd url-shortener
```

### Start Application

```bash
docker compose up -d
```

### Verify Containers

```bash
docker ps
```

---

## Access Application

API:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

OpenAPI Schema:

```text
http://localhost:8000/openapi.json
```

---

## Authentication

### Register

**POST** `/api/v1/auth/register`

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "StrongPassword123"
}
```

### Login

**POST** `/api/v1/auth/login`

```json
{
  "email": "john@example.com",
  "password": "StrongPassword123"
}
```

Response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

---

## API Examples

### Create Short URL

**POST** `/api/v1/urls`

```json
{
  "url": "https://www.example.com"
}
```

Response:

```json
{
  "short_code": "aBc123",
  "short_url": "http://localhost:8000/aBc123"
}
```

---

### Redirect

**GET** `/{short_code}`

```http
GET /aBc123
```

Response:

```http
HTTP/1.1 302 Found
Location: https://www.example.com
```

---

### Analytics

**GET** `/api/v1/analytics/{short_code}`

Response:

```json
{
  "short_code": "aBc123",
  "total_clicks": 42
}
```

---

## Project Structure

```text
url-shortener/
├── app/
├── images/
│   └── architecture.png
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Infrastructure

Infrastructure provisioning and deployment automation are maintained in a separate Terraform repository.

**Terraform Repository**

```text
https://github.com/GowravTata/url-shortener-infra.git
```

The infrastructure repository provisions AWS resources such as:

- EC2 Instance
- IAM Roles and Instance Profile
- Security Groups
- User Data Bootstrapping
- Automated application deployment from GitHub

---

---

## License

MIT License