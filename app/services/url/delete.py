from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenUser, RecordNotFoundError
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.services.url.normalize import normalize_cache_data
from app.services.url.validate import validate
from app.utils.cache_service import CacheService

logger = AppLogger().get_logger()


def delete_short_url(user_id: int, short_code: str, db: Session) -> dict:
    """Soft-delete a short URL owned by the given user and evict it from Redis cache."""
    delete_lock_token = None
    try:
        logger.info(f"Attempting to delete short URL: {short_code}")
        if CacheService.is_patching_flag(short_code):
            logger.warning(f"Short code being patched: {short_code}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Resource is busy",
            )
        delete_lock_token = CacheService.acquire_delete_lock(short_code)

        if not delete_lock_token:
            logger.warning(f"Unable to delete: {short_code}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Resource is busy",
            )
        url_record = (
            db.query(URLModel)
            .filter(
                URLModel.short_code == short_code, URLModel.is_active == True
            )
            .with_for_update()
            .first()
        )

        validate(
            source=url_record,
            short_code=short_code,
            check_user_id=user_id,
        )
        url_record.deleted_at = datetime.now(timezone.utc)
        url_record.deleted_by = user_id
        url_record.is_active = False
        # Mark key as "patching" before edits so concurrent redirects fail fast.

        cached_redirect_data = CacheService.get_redirect_cache(short_code)

        if cached_redirect_data:
            # Reconcile click_count that may not yet be flushed from Redis to DB.
            normalized_cache_data = normalize_cache_data(cached_redirect_data)
            url_record.click_count = normalized_cache_data["click_count"]
        db.commit()

        try:
            CacheService.invalidate_all_url_cache(short_code)
        except Exception:
            logger.warning(f"Redis cleanup failed for {short_code}")
        logger.info(f"Short URL deleted successfully: {short_code}")

        return {"message": "URL deleted successfully"}

    except (RecordNotFoundError, ForbiddenUser, HTTPException):
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        # CacheService.invalidate_deleted_flag_cache(short_code)
        # logger.exception(
        #     f"Error deleting short code: {short_code}, error: {str(e)}"
        # )
        raise
    finally:
        # Always clear delete lock
        if delete_lock_token:
            CacheService.release_delete_lock(
                short_code,
                delete_lock_token,
            )
