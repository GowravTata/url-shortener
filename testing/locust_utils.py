"""Locust scenarios for URL creation and redirect traffic simulation."""

import csv
import json
import logging
import os
import random

from locust import HttpUser, between, task

from app.core.db import get_db
from app.models.url import URLModel

BASEDIR = os.path.dirname(os.path.abspath(__file__))
SHORT_CODES_PATH = os.path.join(BASEDIR, "short_codes.csv")
PAYLOADS_PATH = os.path.join(BASEDIR, "payload.json")
logger = logging.getLogger(__name__)


def load_short_codes():
    """Load short codes from CSV used by redirect tasks."""
    with open(SHORT_CODES_PATH, "r") as f:
        reader = csv.DictReader(f)
        rows = [row["short_code"] for row in reader]
        logger.info("Loaded %s short codes", len(rows))
        return rows


def load_payloads():
    """Load URL creation payloads used by create task."""
    with open(PAYLOADS_PATH, "r") as f:
        payloads = json.load(f)
        logger.info("Loaded %s payloads", len(payloads))
        return payloads


SHORT_CODES = load_short_codes()
PAYLOADS = load_payloads()


def get_short_codes_from_db() -> list:
    db = next(get_db())
    records = (
        db.query(URLModel)
        .filter(URLModel.is_active == True)
        .order_by(URLModel.short_code)
        .all()
    )
    return [obj.short_code for obj in records]


def get_headers():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 Chrome/125.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
    ]
    REFERERS = [
        "https://twitter.com/",
        "https://linkedin.com/",
        "https://google.com/",
    ]
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    referer = random.choice(REFERERS)
    if referer:
        headers["Referer"] = referer
    return headers
