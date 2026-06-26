"""Locust scenarios for URL creation and redirect traffic simulation."""

import random

from locust import HttpUser, task

from testing.locust_utils import PAYLOADS, get_headers, get_short_codes_from_db

SHORT_CODES = get_short_codes_from_db()


class LoadTester(HttpUser):
    @task
    def hit_redirect_serial(self):
        short_code = random.choice(SHORT_CODES)
        headers = get_headers()
        self.client.get(
            f"/{short_code}", headers=headers, allow_redirects=False
        )
