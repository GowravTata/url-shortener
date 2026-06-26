from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import BULK_PATCH_BATCH_SIZE as BATCH_SIZE
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.utils.cache_service import CacheService, chunked

logger = AppLogger().get_logger()


def patch_bulk_urls(
    payload: list,
    user_id: int,
    db: Session,
    disable: bool | None,
    expiry: datetime | None,
):
    total_success = 0
    failure = []
    try:
        to_be_updated = {}
        if isinstance(disable, bool):
            to_be_updated["is_disabled"] = disable
        if expiry:
            try:
                if not isinstance(expiry, datetime):
                    expiry = datetime.fromisoformat(expiry)
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
                else:
                    expiry = expiry.astimezone(timezone.utc)
                to_be_updated["expires_at"] = expiry
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=("Invalid datetime format. " "Use ISO format."),
                )
        if not to_be_updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide disable or expires_at to patch",
            )
        unique_short_codes = list(set(payload))
        # Validate format first
        valid_inputs = []
        for item in unique_short_codes:
            if not isinstance(item, str):
                failure.append(
                    {
                        "item": item,
                        "error": "Invalid format",
                    }
                )
                continue
            valid_inputs.append(item)
        if not valid_inputs:
            return {
                "failure": failure,
                "total_failures": len(failure),
                "total_success": total_success,
                "total": len(payload),
            }
        # Validate existence in batches
        existing_set = set()
        for batch in chunked(valid_inputs, BATCH_SIZE):
            rows = (
                db.query(URLModel.short_code)
                .filter(
                    URLModel.user_id == user_id,
                    URLModel.is_active.is_(True),
                    URLModel.short_code.in_(batch),
                )
                .all()
            )
            existing_set.update(row[0] for row in rows)
        invalid_codes = set(valid_inputs) - existing_set
        for code in invalid_codes:
            failure.append(
                {
                    "item": code,
                    "error": "Short Code Not Found",
                }
            )
        valid_short_codes = list(existing_set)
        # Process in batches
        for batch in chunked(valid_short_codes, BATCH_SIZE):
            lock_manager = CacheService()
            try:
                # Prevent patch/delete races
                delete_flags = CacheService.get_delete_flags_bulk(batch)
                delete_map = dict(zip(batch, delete_flags))
                filtered_batch = []
                for code in batch:
                    if delete_map.get(code):
                        failure.append(
                            {"item": code, "error": ("Resource Busy")}
                        )
                        continue
                    filtered_batch.append(code)
                if not filtered_batch:
                    continue
                acquired, locked = CacheService.acquire_patch_lock_bulk(
                    filtered_batch
                )
                final_valid = []
                for code in locked:
                    failure.append({"item": code, "error": "LOCKED"})
                for code, token in acquired:
                    lock_manager.acquired_locks.append((code, token))
                    final_valid.append(code)
                if not final_valid:
                    continue
                stmt = (
                    update(URLModel)
                    .where(
                        URLModel.short_code.in_(final_valid),
                        URLModel.user_id == user_id,
                        URLModel.is_active.is_(True),
                    )
                    .values(**to_be_updated)
                )
                result = db.execute(stmt)
                db.commit()
                total_success += result.rowcount
                try:
                    CacheService.invalidate_short_codes_bulk(final_valid)
                except Exception:
                    logger.warning("Failed cache invalidation")
                logger.info(
                    f"Patched batch={len(final_valid)} "
                    f"updated={result.rowcount}"
                )
            except Exception:
                db.rollback()
                raise
            finally:
                try:
                    lock_manager.release_patch_lock_bulk()
                except Exception:
                    pass

        return {
            "failure": failure[:1000],
            "total_failures": len(failure),
            "total_success": total_success,
            "total": len(payload),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Bulk patch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
