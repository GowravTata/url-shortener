import time
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import BULK_CREATE_BATCH_SIZE as BATCH_SIZE
from app.core.config import DOMAIN
from app.core.exceptions import CodeGenerationError
from app.core.logging import AppLogger
from app.models.url import URLModel
from app.schemas.url import ShortenRequest
from app.services.common.expiry import get_expiry_date
from app.utils.cache_service import chunked
from app.utils.generators import generate_code

logger = AppLogger().get_logger()


def generate_unique_code(existing_alias: set, max_retries: int = 5) -> str:
    """
    Generate a unique short code.
    """
    for _ in range(max_retries):
        code = generate_code().lower()
        if code not in existing_alias:
            existing_alias.add(code)
            return code

    raise CodeGenerationError(
        message=("Failed to generate unique short code after retries"),
        code="CODE_GENERATION_FAILED",
    )


def shorten_bulk_url(payload: list, user_id: int, db: Session) -> dict:
    records = []
    failure = []
    try:
        logger.info(
            f"Processing bulk shorten request "
            f"user_id={user_id} "
            f"count={len(payload)}"
        )
        total_start = time.perf_counter()
        valid_inputs = []
        for batch in chunked(payload, BATCH_SIZE):
            for item in batch:
                try:
                    ShortenRequest.model_validate(item)
                    valid_inputs.append(item)
                except ValidationError as e:
                    for err in e.errors():
                        field = ".".join(str(loc) for loc in err["loc"])
                        msg = err["msg"]
                        failure.append(
                            {
                                "item": item,
                                "error": (f"{field}: {msg}"),
                            }
                        )
        logger.info(f"Validated inputs=" f"{len(valid_inputs)}")
        if not valid_inputs:
            return {
                "failure": failure[:1000],
                "total_failures": len(failure),
                "total_success": 0,
                "total": len(payload),
            }
        incoming_aliases = []
        for item in valid_inputs:
            alias = item.get("custom_alias")
            if alias:
                incoming_aliases.append(alias.lower())
        used_codes = set()
        for batch in chunked(
            incoming_aliases,
            BATCH_SIZE,
        ):
            existing_aliases = (
                db.query(URLModel.short_code)
                .filter(URLModel.short_code.in_(batch))
                .all()
            )
            used_codes.update(row[0] for row in existing_aliases)
        seen_alias = set()
        created_at = datetime.now(timezone.utc)
        expires_at = get_expiry_date()
        for batch in chunked(valid_inputs, BATCH_SIZE):
            for item in batch:
                original_url = item.get("original_url")
                custom_alias = item.get("custom_alias")
                expiry = item.get("expiry")
                if custom_alias:
                    custom_alias = custom_alias.lower()
                    if custom_alias in seen_alias:
                        failure.append(
                            {
                                "item": item,
                                "error": ("Alias already " "exists in request"),
                            }
                        )
                        continue
                    if custom_alias in used_codes:
                        failure.append(
                            {"item": item, "error": ("Alias already " "exists")}
                        )
                        continue
                    seen_alias.add(custom_alias)
                try:
                    if expiry:
                        expires_at = get_expiry_date(expiry)
                except HTTPException:
                    failure.append(
                        {
                            "item": item,
                            "error": ("Invalid expiry"),
                        }
                    )
                    continue
                if custom_alias:
                    short_code = custom_alias
                else:
                    short_code = generate_unique_code(
                        existing_alias=(used_codes)
                    )
                record = {
                    "user_id": user_id,
                    "original_url": (original_url),
                    "short_code": short_code,
                    "expires_at": expires_at,
                    "created_at": created_at,
                    "is_active": True,
                }

                records.append(record)
        logger.info(f"Prepared records={len(records)}")
        total_inserted = 0
        for batch in chunked(records, BATCH_SIZE):
            MAX_RETRIES = 3
            for attempt in range(MAX_RETRIES):
                try:
                    db.bulk_insert_mappings(
                        URLModel,
                        batch,
                    )
                    db.commit()
                    total_inserted += len(batch)
                    break
                except IntegrityError as e:
                    db.rollback()
                    if attempt == MAX_RETRIES - 1:
                        failure.extend(
                            [
                                {
                                    "item": (row["original_url"]),
                                    "error": (
                                        "Failed to " "generate " "unique code"
                                    ),
                                }
                                for row in batch
                            ]
                        )
                        break
                    for row in batch:
                        generated = row["short_code"] not in seen_alias
                        if generated:
                            new_code = generate_unique_code(used_codes)
                            row["short_code"] = new_code
                            row["short_url"] = f"{DOMAIN}/" f"{new_code}"
        logger.info(f"Inserted rows=" f"{total_inserted}")
        logger.info(
            f"Bulk shorten completed "
            f"in "
            f"{time.perf_counter() - total_start}"
            f" seconds"
        )
        return {
            "failure": failure[:1000],
            "total_failures": len(failure),
            "total_success": total_inserted,
            "total": len(payload),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(
            f"Bulk shorten failed " f"user_id={user_id} " f"error={str(e)}"
        )
        raise HTTPException(
            status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail="Internal server error",
        )
