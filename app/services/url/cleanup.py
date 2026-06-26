from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.logging import AppLogger
from app.models.url import URLModel
from app.utils.cache_service import CacheService

logger = AppLogger().get_logger()


def deactivate_expired_urls(db: Session, batch_size: int = 100):
    """Celery task to clean up expired URLs from the database and Redis cache."""
    try:
        logger.info("Starting cleanup of expired URLs.")
        # Query for expired URLs
        now = datetime.now(timezone.utc)
        records = (
            db.query(URLModel)
            .filter(
                URLModel.expires_at < now,
                URLModel.is_active.is_(True),
            )
            .limit(batch_size)
            .all()
        )
        if not records:
            logger.info("No records to clean up.")
            return {"message": "No records to clean up"}
        logger.info("Found %s expired URLs for cleanup", len(records))
        for url in records:
            # Soft-disable expired URLs so historical analytics remain queryable.
            url.is_disabled = True
            url.is_active = False
            # Drop redirect cache so future reads cannot serve expired URLs.
            try:
                CacheService.invalidate_redirect_cache(
                    short_code=url.short_code
                )
            except Exception:
                logger.warning(
                    f"Error Occured while invalidating cache: {url.short_code}"
                )
        db.commit()
        return {"message": "Cleaned up the Expired URLS from DB"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup: {e}")
    finally:
        logger.info("Finished cleanup of expired URLs.")
        db.close()
