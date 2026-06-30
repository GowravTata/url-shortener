"""Send sample URL creation requests to a local service instance."""

import json

import requests
from sqlalchemy import text

from app.core.config import TOPICS
from app.core.db import get_db
from app.core.db import redis_conn as redis
from app.models.url import URLModel

db = next(get_db())

url = "http://amazon.com"
PORT = 8000
LIMIT = 5
DOMAIN = f"http://localhost:{PORT}"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def get_all_data() -> dict:
    db = next(get_db())
    records = db.query(URLModel).order_by(URLModel.short_code).all()
    payloads = []
    for obj in records:
        payloads.append(obj.short_code)
    return {"short_codes": payloads}


def generate_create_data(url, limit):
    payloads = []
    for i in range(1, limit + 1):
        payloads.append({"original_url": url, "custom_alias": f"az{i}"})
    total_payload = {"urls": payloads}
    return total_payload


def send_post_data(url, headers, payload) -> dict | str:
    response = requests.post(url=url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to add data")
        return response.text


def generate_patch_data():
    payload = get_all_data()
    total_payload = {
        "short_codes": payload.get("short_codes"),
        "expires_at": "2026-06-30T16:28:25.337Z",
    }
    return total_payload


def generate_redirect_data(limit):
    payload = get_all_data()
    return {
        "short_codes": payload.get("short_codes"),
    }


def wipeout_db():
    db = next(get_db())
    db.execute(text("TRUNCATE TABLE urls,click_events RESTART IDENTITY"))
    db.commit()
    redis.flushall()
    return "Data Wiped Successfully"


def get_token():
    url = f"{DOMAIN}/v1/auth/login-json"
    payload = {"email": "gowravtata@fastapi.com", "password": "secretpassword"}
    output: dict | str = send_post_data(url, headers, payload)
    return output.get("access_token") if isinstance(output, dict) else output


def load_data_into_db(limit=LIMIT):
    payload = generate_create_data(url=url, limit=limit)
    post_url = f"{DOMAIN}/v1/urls/bulk"
    token = get_token()
    headers["Authorization"] = f"Bearer {token}"
    send_post_data(post_url, headers, payload)
    return "Data Loaded Successfully"


def purge_kafka_topic(topic=TOPICS):
    put_url = f"{DOMAIN}/v1/kafka/{topic}"
    token = get_token()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.put(url=put_url, headers=headers)
    if response.status_code == 200:
        return f"Topic Purged Successfully"
    else:
        print("Failed to purge topic")
        return response.text


allowed_methods = [
    "create",
    "patch",
    "redirect",
    "delete",
    "wipeout_db",
    "load_data",
    "reset_and_load_data",
]

METHOD = "reset_and_load_data"
limit = 1000
data = None
if METHOD not in allowed_methods:
    print("Provide a valid input")
if METHOD == "create":
    data = generate_create_data(url, limit)
if METHOD == "patch":
    data = generate_patch_data()
if METHOD in ("redirect", "delete"):
    data = generate_redirect_data(limit)
if METHOD == "all_short_codes_from_db":
    data = get_all_data()
if METHOD == "wipeout_db":
    print(wipeout_db())
if METHOD == "load_data":
    load_data_into_db(limit=25)
if METHOD == "reset_and_load_data":
    print(wipeout_db())
    print(load_data_into_db(limit=15))
    print(purge_kafka_topic())


