from datetime import datetime

from sqlalchemy import or_

from app.core.celery_app import celery_app
from app.core.db import get_db
from app.core.db import redis_conn as redis
from app.core.logging import AppLogger
from app.models.url import URLModel

logger = AppLogger().get_logger()


@celery_app.task
def deactivate_expired_urls(batch_size: int = 100):
    """Celery task to clean up expired URLs from the database and Redis cache."""
    db = next(get_db())
    try:
        logger.info("Starting cleanup of expired URLs.")
        # Query for expired URLs
        now = datetime.utcnow()
        records = (
            db.query(URLModel)
            .filter(
                or_(
                    URLModel.expires_at < now,
                    URLModel.is_active.is_(True),
                )
            )
            .limit(batch_size)
            .all()
        )
        if not records:
            logger.info("No records to clean up.")
            return
        logger.info("Reached here, expired urls are %s", records)
        for record in records:
            logger.info(f"Cleaning up URL with short code: {record.short_code}")
            print(record)
        for url in records:
            # Remove cached redirect fields before deleting the DB row.
            redis.hdel(
                f"url:{url.short_code}",
                "original_url",
                "expires_at",
                "click_count",
                "last_accessed",
                "is_active",
                "created_at",
            )
            # Hard-delete expired rows in this background cleanup task.
            db.delete(url)
        db.commit()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    finally:
        logger.info("Finished cleanup of expired URLs.")
        db.close()
