from datetime import datetime, timezone

from app.core.exceptions import RecordNotFoundError
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.utils.cache_service import CacheService
from app.utils.serializers import serialize_url_for_cache

logger = AppLogger().get_logger()


def restore_short_code(user_id, short_code, db):
    try:
        url_record = (
            db.query(URLModel)
            .filter(
                URLModel.user_id == user_id, URLModel.short_code == short_code
            )
            .first()
        )
        if not url_record:
            logger.info(f"Record Does not exist")
            raise RecordNotFoundError(
                message="Not found",
                code="NOT FOUND",
                context={"msg": "Record not found"},
            )
        if url_record.is_active:
            logger.info("Record is already active")
            raise
        url_record.is_active = True
        url_record.deleted_at = None
        url_record.deleted_by = None
        # Update the Cache
        db.commit()
        if url_record.expires_at:
            ttl = max(
                0,
                int(
                    (
                        url_record.expires_at - datetime.now(timezone.utc)
                    ).total_seconds()
                ),
            )
        else:
            ttl = None
        mapping = serialize_url_for_cache(source=url_record)
        CacheService.set_redirect_cache(
            short_code=short_code, mapping=mapping, ttl=ttl
        )
        return {"Msg": "Short Code Restored Successfully"}
    except RecordNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error in restoring the short code : {e}")
        raise
