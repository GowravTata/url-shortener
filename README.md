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
* RESTful APIs
* OpenAPI/Swagger documentation

---

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* Redis
* Docker
* Docker Compose

---

## Architecture

The application uses FastAPI as the core backend service, PostgreSQL for persistence, Redis for caching, and an event-driven analytics pipeline for click tracking and reporting.

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
                        v
                Analytics Updated
```

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
302 Found
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
└── README.md
```

---

## Running Tests

```bash
docker compose exec app pytest
```

---

## Infrastructure

Infrastructure provisioning and deployment automation are maintained separately.

Terraform Repository:

```text
https://git-codecommit.ap-south-2.amazonaws.com/v1/repos/url-shortener-infra
```

---

## License

MIT License
