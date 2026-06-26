from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (ForbiddenUser, RecordNotFoundError,
                                 URLDeletedError, URLDisabledError,
                                 URLExpiredError)
from app.core.logging import AppLogger
from app.services.url.validate import validate
from app.utils.cache_service import CacheService
from app.utils.url_repository import get_url_by_short_code

logger = AppLogger().get_logger()

ANALYTICS_CACHE_TTL = 15


def get_short_code_analytics(
    short_code: str, user_id: int, db: Session
) -> dict:
    """
    Returns analytics in required response format.
    """

    logger.info(f"Fetching analytics for short_code={short_code}")

    try:
        cached_analytics_data = CacheService.get_analytics_cache(short_code)

        if cached_analytics_data:
            logger.info(f"Analytics cache hit for {short_code}")
            validate(
                source=cached_analytics_data,
                short_code=short_code,
                check_user_id=user_id,
            )
            return cached_analytics_data

        logger.info(f"Analytics cache miss for {short_code}")

        # Fetching Data from database
        analytics_record = get_url_by_short_code(
            db=db, short_code=short_code, include_deleted=True
        )

        if not analytics_record:
            raise RecordNotFoundError(
                message="URL not found",
                context={"short_code": short_code},
            )
        validate(
            source=analytics_record,
            short_code=short_code,
            check_user_id=user_id,
            allow_expired=True,
            allow_disabled=True,
        )

        # Derive a human-readable lifecycle status from DB flags and expiry.
        status = "active"

        if not analytics_record.is_active:
            status = "deleted"
        elif analytics_record.is_disabled:
            status = "disabled"

        elif (
            analytics_record.expires_at
            and analytics_record.expires_at < datetime.now(timezone.utc)
        ):
            status = "expired"

        # Redis can have fresher interaction metrics than DB between flushes.
        cached_redirect_data = CacheService.get_redirect_cache(short_code)
        redis_last_accessed = ""
        if cached_redirect_data:
            redis_last_accessed = cached_redirect_data.get("last_accessed", "")
        final_last_accessed = analytics_record.last_accessed
        if redis_last_accessed:
            # Keep the most recent last_accessed value from either source.
            if not isinstance(redis_last_accessed, datetime):
                redis_last_accessed = datetime.fromisoformat(
                    redis_last_accessed
                )
            if redis_last_accessed is None:
                redis_last_accessed = redis_last_accessed.replace(
                    tzinfo=timezone.utc
                )
            if (
                not final_last_accessed
                or redis_last_accessed > final_last_accessed
            ):
                final_last_accessed = redis_last_accessed
        response = {
            "original_url": analytics_record.original_url,
            "created_at": analytics_record.created_at.isoformat(),
            "expires_at": (
                analytics_record.expires_at.isoformat()
                if analytics_record.expires_at
                else None
            ),
            "is_active": analytics_record.is_active,
            "click_count": analytics_record.click_count,
            "last_accessed": (
                final_last_accessed.isoformat() if final_last_accessed else None
            ),
            "status": status,
            "is_disabled": analytics_record.is_disabled,
            "user_id": analytics_record.user_id,
        }
        # Cache Analytics in Redis with a TTL
        CacheService.set_analytics_cache(
            short_code=short_code,
            response=response,
            ttl=ANALYTICS_CACHE_TTL,
        )

        logger.info(
            f"Analytics cached for {short_code} with TTL={ANALYTICS_CACHE_TTL}s"
        )

        return response
    except (
        URLDisabledError,
        RecordNotFoundError,
        URLDeletedError,
        URLExpiredError,
        ForbiddenUser,
    ):
        raise

    except Exception as e:
        logger.exception(
            f"Unexpected error fetching analytics for {short_code}: {str(e)}"
        )
        raise
