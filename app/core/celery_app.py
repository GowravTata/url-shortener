"""Celery application setup and periodic task schedule."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import (REDIS_HOST, REDIS_PASSWORD, REDIS_PORT,
                             REDIS_USERNAME)

celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0",
    include=[
        "app.tasks.url.cleanup",
        "app.tasks.url.db_flush"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "flush-db-every-30-minutes": {
        "task": "app.tasks.url.db_flush.flush_db",
        "schedule": crontab(minute="*/2"),  # every 30 minutes
    },
}
