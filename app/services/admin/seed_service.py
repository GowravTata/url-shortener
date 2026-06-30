import os
import random

import requests
from faker import Faker
from fastapi import HTTPException

from app.core.db import get_db
from app.models.url import URLModel
from app.models.user import Users
from app.services.admin.seed_data import ALL_URLS

fake = Faker()

DOMAIN = os.getenv("API_BASE_URL", "http://localhost:8000")

REGISTER_USER_API = f"{DOMAIN}/v1/auth/register_user"
LOGIN_USER_API = f"{DOMAIN}/v1/auth/login-json"
CREATE_URL_API = f"{DOMAIN}/v1/urls/"

PASSWORD = "secretpassword"


def get_users():
    db = next(get_db())
    try:
        return [user.email for user in db.query(Users).all()]
    finally:
        db.close()


def get_short_urls():
    db = next(get_db())
    try:
        return [url.short_code for url in db.query(URLModel).all()]
    finally:
        db.close()


def validate_users_exist():
    users = get_users()
    if not users:
        raise HTTPException(
            status_code=400,
            detail="No users found. Seed users before creating URLs.",
        )

    return users


def validate_urls_exist():
    urls = get_short_urls()

    if not urls:
        raise HTTPException(
            status_code=400,
            detail="No URLs found. Seed URLs before generating clicks.",
        )

    return urls


def generate_emails(total_users: int):
    emails = set()

    while len(emails) < total_users:
        emails.add(
            f"{fake.first_name().lower()}."
            f"{fake.last_name().lower()}@fastapi.com"
        )

    return list(emails)


def create_users(total_users: int):
    created = 0

    for email in generate_emails(total_users):
        response = requests.post(
            REGISTER_USER_API,
            json={
                "email": email,
                "password": PASSWORD,
            },
            timeout=10,
        )

        if response.status_code == 200:
            created += 1

    return created


def login(email: str):
    response = requests.post(
        LOGIN_USER_API,
        json={
            "email": email,
            "password": PASSWORD,
        },
        timeout=10,
    )
    if response.status_code != 200:
        return None
    return response.json()["access_token"]


def create_urls(total_urls: int):
    users = validate_users_exist()
    success = 0
    for _ in range(total_urls):
        email = random.choice(users)
        original_url = random.choice(ALL_URLS)
        token = login(email)
        if token is None:
            continue
        response = requests.post(
            CREATE_URL_API,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "original_url": original_url,
            },
            timeout=10,
        )
        if response.status_code == 200:
            success += 1
    return success


def generate_clicks(total_clicks: int):
    short_urls = validate_urls_exist()
    success = 0
    for _ in range(total_clicks):
        short_code = random.choice(short_urls)
        response = requests.get(
            f"{DOMAIN}/{short_code}",
            allow_redirects=False,
            timeout=10,
        )
        if response.status_code in (200, 301, 302, 307, 308):
            success += 1
    return success
