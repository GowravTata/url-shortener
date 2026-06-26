from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.config import URL_DOESNOT_EXIST, USER_FORBIDDEN_ERROR
from app.core.exceptions import (ForbiddenUser, RecordNotFoundError,
                                 URLDisabledError, URLExpiredError)
from app.core.logging import AppLogger

logger = AppLogger().get_logger()


def validate(
    source,
    short_code: str,
    check_disabled: bool = False,
    check_expiry: bool = True,
    check_user_id: int | None = None,
    allow_expired: bool = False,
    allow_disabled: bool = False,
) -> bool:
    """
    Validate a URL record (from DB or Redis cache) against common business rules.

    Raises the appropriate AppError subclass if any check fails:
    - RecordNotFoundError  - record is missing
    - URLDisabledError  - URL has been disabled
    - ForbiddenUser     - authenticated user does not own the URL
    - URLExpiredError   - URL has passed its expiry date
    """
    try:
        if not source:
            logger.warning(f"Record not found: {short_code}")
            raise RecordNotFoundError(
                message=URL_DOESNOT_EXIST,
                code=URL_DOESNOT_EXIST,
                context={"short_code": short_code},
            )

        # Accept both ORM objects and normalized cache dicts through one path.
        is_disabled = (
            source["is_disabled"]
            if isinstance(source, dict)
            else source.is_disabled
        )
        expires_at = (
            source["expires_at"]
            if isinstance(source, dict)
            else source.expires_at
        )
        user_id = (
            source["user_id"] if isinstance(source, dict) else source.user_id
        )

        # Disabled
        if check_disabled and is_disabled and not allow_disabled:
            logger.warning(f"URL is disabled: {short_code}")
            raise URLDisabledError(
                message="URL Disabled",
                context={"short_code": short_code},
            )

        # Ownership
        if check_user_id is not None:
            if not user_id or int(user_id) != int(check_user_id):
                logger.warning(f"User forbidden for: {short_code}")
                raise ForbiddenUser(
                    message=USER_FORBIDDEN_ERROR,
                    code="USER_FORBIDDEN_TO_ACCESS",
                    context={"user_id": check_user_id},
                )

        # Expiry
        if check_expiry and expires_at:
            now = datetime.now(timezone.utc)
            # Cache payloads may carry ISO strings, ORM records carry datetimes.
            if not isinstance(expires_at, datetime):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at < now and not allow_expired:
                logger.warning(f"URL expired: {short_code}")
                raise URLExpiredError(
                    message="URL expired",
                    context={"short_code": short_code},
                )

        return True

    except (
        RecordNotFoundError,
        URLDisabledError,
        URLExpiredError,
        ForbiddenUser,
    ):
        raise

    except Exception as e:
        logger.exception(
            f"Unexpected validation error for key: {short_code}. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
