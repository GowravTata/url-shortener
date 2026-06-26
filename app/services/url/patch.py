from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (ForbiddenUser, InvalidParameter,
                                 RecordNotFoundError, URLDeletedError)
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.services.url.normalize import normalize_cache_data
from app.services.url.validate import validate
from app.utils.cache_service import CacheService

logger = AppLogger().get_logger()


def patch_short_url(
    user_id: int,
    expires_at: datetime | None,
    disable: bool | None,
    short_code: str,
    db: Session,
) -> dict:
    """
    Update the expiry date and/or disabled state of an existing short URL.

    At least one of `expires_at` or `disable` must be provided.  The Redis
    cache entry is invalidated before the database record is updated.
    """
    patch_lock_token = None
    try:

        if expires_at is None and disable is None:
            logger.error(
                f"Invalid Parameter for performing patching short code: {short_code}"
            )
            raise InvalidParameter(
                message=f"Invalid Parameter for patching short code: {short_code}",
                code="INVALID_PARAMETER_EXCEPTION",
                context={
                    "msg": "Provide at least one of expires_at or disable"
                },
            )

        if CacheService.is_deleted_flag(short_code) is not None:
            logger.warning(f"Short code being deleted: {short_code}")
            raise URLDeletedError(
                message="URL is deleted",
                context={"short_code": short_code},
            )

        # Mark key as "patching" before edits so concurrent redirects fail fast.
        patch_lock_token = CacheService.acquire_patch_lock(short_code)

        if not patch_lock_token:
            logger.warning(f"Short code being patched: {short_code}")
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
            allow_expired=True,
            allow_disabled=True,
        )

        CacheService.invalidate_redirect_cache(short_code)

        if expires_at is not None:
            now = datetime.now(timezone.utc)
            if not isinstance(expires_at, datetime):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < now:
                logger.warning(
                    f"Provided expiry date {expires_at} is in the past"
                )
                raise InvalidParameter(
                    message="Expiry mentioned in the past",
                    code="INVALID_PARAMETER_EXCEPTION",
                    context={
                        "msg": "Provide at least one of expires_at or disable"
                    },
                )
            url_record.expires_at = expires_at
        if disable is not None:
            if not isinstance(disable, bool):
                logger.warning(
                    f"Invalid disable value '{disable}' for short_code: {short_code}"
                )
                raise InvalidParameter(
                    message="Invalid Disable Parameter",
                    code="INVALID_PARAMETER_EXCEPTION",
                    context={"msg": "True, False are the Only Valid values"},
                )
            url_record.is_disabled = disable
        cached_redirect_data = CacheService.get_redirect_cache(short_code)
        if cached_redirect_data:
            # Preserve buffered click_count before cache is fully invalidated.
            normalized_cache_data = normalize_cache_data(cached_redirect_data)
            url_record.click_count = normalized_cache_data["click_count"]
        db.commit()

        try:
            CacheService.invalidate_all_url_cache(short_code)
        except Exception:
            logger.warning(f"Failed to delete cache for {short_code}")

        logger.info(f"Short Code Updated Successfully for {short_code}")
        return {"message": "Short Code Updated Successfully"}
    except (
        InvalidParameter,
        URLDeletedError,
        RecordNotFoundError,
        ForbiddenUser,
    ):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Error occured while patching short {short_code}, error :{e.args}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        # Always clear patch lock so redirects are restored after success/failure.
        if patch_lock_token:
            CacheService.release_patch_lock(
                short_code,
                patch_lock_token,
            )
