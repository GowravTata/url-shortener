from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import BULK_DELETE_BATCH_SIZE as BATCH_SIZE
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.utils.cache_service import CacheService, chunked

logger = AppLogger().get_logger()


def delete_bulk_urls(payload: list, user_id: int, db: Session):
    total_success = 0
    failure = []
    unique_short_codes = list(set(payload))
    try:
        valid_inputs = []
        patch_flags = CacheService.get_patching_flags_bulk(unique_short_codes)
        patch_map = dict(zip(unique_short_codes, patch_flags))
        for item in unique_short_codes:
            if not isinstance(item, str):
                failure.append(
                    {
                        "item": item,
                        "error": "Invalid format",
                    }
                )
                continue
            if patch_map.get(item):
                failure.append(
                    {
                        "item": item,
                        "error": "Resource busy",
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

        invalid_short_codes = set(valid_inputs) - existing_set
        for code in invalid_short_codes:
            failure.append({"item": code, "error": "Not Found"})
        valid_short_codes = list(existing_set)
        if not valid_short_codes:
            return {
                "failure": failure,
                "total_failures": len(failure),
                "total_success": total_success,
                "total": len(payload),
            }
        # Process delete in batches
        for batch in chunked(valid_short_codes, BATCH_SIZE):
            lock_manager = CacheService()
            try:
                acquired, locked = CacheService.acquire_delete_lock_bulk(batch)
                final_valid = []
                for code in locked:
                    failure.append(
                        {
                            "item": code,
                            "error": "LOCKED",
                        }
                    )
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
                    .values(
                        is_active=False,
                        deleted_at=datetime.now(timezone.utc),
                        deleted_by=user_id,
                    )
                )
                result = db.execute(stmt)
                db.commit()
                total_success += result.rowcount
                CacheService.invalidate_redirect_cache_bulk(final_valid)
                logger.info(
                    f"Deleted batch size={len(final_valid)} "
                    f"updated={result.rowcount}"
                )
            except Exception:
                db.rollback()
                raise
            finally:
                try:
                    lock_manager.release_delete_lock_bulk()
                except Exception:
                    pass
        return {
            "total_failures": len(failure),
            "total_success": total_success,
            "total": len(payload),
            "failure": failure[:1000],
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Bulk delete failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
