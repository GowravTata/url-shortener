from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (ForbiddenUser, RecordNotFoundError,
                                 URLDeletedError, URLDisabledError,
                                 URLExpiredError)
from app.core.logging import AppLogger
from app.services.url.normalize import normalize_cache_data
from app.services.url.validate import validate
from app.utils.cache_service import CacheService
from app.utils.serializers import (serialize_url_for_cache,
                                   serialize_url_metadata_response)
from app.utils.url_repository import get_url_by_short_code

logger = AppLogger().get_logger()


def get_short_code_info(short_code: str, user_id: int, db: Session) -> dict:
    """Retrieve metadata for a short URL, checking Redis first then falling back to the database."""
    logger.info(f"Retrieving info for short code: {short_code}")

    try:
        # Redis first
        cached_redirect_data = CacheService.get_redirect_cache(short_code)

        if cached_redirect_data:
            logger.info(f"Cache hit for short code: {short_code}")
            # Normalize Redis hash values before applying shared validation rules.
            normalized_cache_data = normalize_cache_data(
                source=cached_redirect_data
            )
            validate(
                source=normalized_cache_data,
                short_code=short_code,
                check_user_id=user_id,
            )

            metadata = serialize_url_metadata_response(normalized_cache_data)

            return metadata

        # DB fallback
        url_record = get_url_by_short_code(db=db, short_code=short_code)
        validate(
            source=url_record,
            short_code=short_code,
            check_user_id=user_id,
        )
        # Lazy-fill cache from DB so subsequent reads avoid hitting Postgres.
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

        mapping = serialize_url_for_cache(url_record)
        CacheService.set_redirect_cache(short_code, mapping, ttl)

        logger.info(f"Cached short code: {short_code}")

        metadata = serialize_url_metadata_response(
            serialize_url_for_cache(url_record)
        )
        return metadata
    except (
        RecordNotFoundError,
        URLExpiredError,
        URLDisabledError,
        URLDeletedError,
        ForbiddenUser,
    ):
        raise

    except Exception as e:
        logger.exception(
            f"Unexpected error for short_code={short_code}: {str(e)}"
        )
        raise
