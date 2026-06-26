from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic import AnyHttpUrl
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import DOMAIN, URL_SHORTENED_SUCCESSFULLY
from app.core.exceptions import AliasNotAvailable, CodeGenerationError
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.services.common.expiry import get_expiry_date
from app.utils.cache_service import CacheService
from app.utils.generators import generate_code
from app.utils.serializers import serialize_url_for_cache

logger = AppLogger().get_logger()


def generate_unique_code(db: Session, max_retries: int = 5) -> str:
    """
    Generate a unique short_code by checking DB.
    """
    for _ in range(max_retries):
        code = generate_code()
        # Check if the generated code already exists in the database
        exists = (
            db.query(URLModel.id).filter(URLModel.short_code == code).first()
        )
        # If it doesn't exist, return the code
        if not exists:
            return code.lower()

    raise CodeGenerationError(
        message="Failed to generate unique short code after retries",
        code="CODE_GENERATION_FAILED",
    )


def shorten_url(
    original_url: str,
    custom_alias: str | None,
    expiry: str | datetime | None,
    user_id: int,
    db: Session,
) -> dict:
    """
    Validate and shorten a URL, storing it in the database and caching it in Redis.

    Uses a custom alias if provided (after checking it is not reserved), otherwise
    auto-generates a unique Base62 short code.  Returns the resulting short URL
    and short code on success.
    """
    try:
        original_url = str(original_url)
        expires_at = get_expiry_date(expiry)
        # Respect caller-supplied alias; otherwise generate a collision-checked code.
        if custom_alias:
            short_code = custom_alias
        else:
            short_code = generate_unique_code(db)
        # Inserting the new record into the database
        created_at = now = datetime.now(timezone.utc)
        new_entry = URLModel(
            user_id=user_id,
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at,
            created_at=created_at,
            is_active=True,
        )

        db.add(new_entry)
        db.commit()
        logger.info(
            f"New URL entry added to database with short code: {short_code}"
        )
        # Store all the data in a single Redis hash for efficient retrieval
        # and management
        logger.info(
            f"Caching new URL entry in Redis with key: url:{short_code}"
        )
        # Align Redis TTL with expiry to let cache self-expire with business state.
        if expires_at:
            ttl = max(0, int((expires_at - now).total_seconds()))
        else:
            ttl = None

        # Serialize the data for caching
        mapping = serialize_url_for_cache(new_entry)
        # Cache the key
        CacheService.set_redirect_cache(short_code, mapping, ttl)

        return {
            "message": URL_SHORTENED_SUCCESSFULLY,
            "short_code": short_code,
        }

    except IntegrityError as e:
        db.rollback()
        logger.warning(
            f"IntegrityError occurred while shortening URL: {str(e)}"
        )
        raise AliasNotAvailable(
            message="Alias is not available",
            code="ALIAS_NOT_AVAILABLE",
            context={"custom_alias": custom_alias},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error occurred while shortening URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
