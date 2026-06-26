import random
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import MY_IP, TOPICS
from app.core.exceptions import (RecordNotFoundError, URLDeletedError,
                                 URLDisabledError, URLExpiredError)
from app.core.logging import AppLogger
from app.kafka.producer import kafka_client_obj
from app.services.url.normalize import normalize_cache_data
from app.services.url.validate import validate
from app.utils.cache_service import CacheService
from app.utils.url_repository import get_url_by_short_code

logger = AppLogger().get_logger()


def build_analytics_data(user_id, short_code, request, latency_ms, cache_hit):
    return {
        "event_id": str(uuid4()),
        "user_id": user_id,
        "short_code": short_code,
        "clicked_at": datetime.now(timezone.utc),
        "ip_address": random.choice(MY_IP),
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
        "request_method": request.method,
        "cache_hit": cache_hit,
        "redirect_latency_ms": latency_ms,
    }


def get_original_url(
    short_code: str,
    db: Session,
    request,
):
    """
    Retrieve the Orignal URL for a given short URL if it exists.
    """
    try:
        start = time.perf_counter()
        # First check Redis cache for the key
        logger.info(f"Looking up key: {short_code} in Redis cache")
        cached: Dict | None = CacheService.get_redirect_cache(short_code)
        # Guard reads while delete flow is in progress to avoid serving stale data.
        if CacheService.is_deleted_flag(short_code):
            logger.warning(f"Short code being deleted: {short_code}")
            raise URLDeletedError(
                message="URL is deleted",
                context={"short_code": short_code},
            )

        # Patch flow marks the key as temporarily unavailable until write completes.
        if CacheService.is_patching_flag(short_code):
            logger.warning(f"Short code being patched: {short_code}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="URL is being updated, try again shortly",
            )

        now = datetime.now(timezone.utc)
        if cached:
            logger.info(f"Cache hit for key: {short_code}")
            data = normalize_cache_data(cached)
            validate(
                source=data,
                short_code=short_code,
                check_disabled=True,
                check_expiry=True,
            )

            # Drop expired cache entries opportunistically on read.
            if data["expires_at"] and data["expires_at"] < datetime.now(
                timezone.utc
            ):
                CacheService.invalidate_redirect_cache(short_code=short_code)
            # Click metrics are buffered in Redis and flushed later by worker jobs.
            RedirectResponse(
                url=data["original_url"],
                status_code=status.HTTP_302_FOUND,
            )

            latency_ms = (time.perf_counter() - start) * 1000
            # Build the data for Analytics
            analytics_data = build_analytics_data(
                user_id=cached.get("user_id"),
                short_code=short_code,
                request=request,
                latency_ms=latency_ms,
                cache_hit=True,
            )
            threading.Thread(
                target=kafka_client_obj.publish_event,
                args=(TOPICS, short_code, analytics_data),
                daemon=True,
            ).start()
            return {"message": "Successful"}
        logger.info(f"Cache miss for key: {short_code}. Checking database...")
        record: Any = get_url_by_short_code(db=db, short_code=short_code)
        validate(
            source=record,
            short_code=short_code,
            check_disabled=True,
            check_expiry=True,
        )

        # If found in DB, cache the result and return it
        logger.info(
            f"Record found in database for key: {record.short_code}. Caching "
            f"result and returning value."
        )
        result_value = record.original_url
        # Cache the result in Redis for future lookups
        logger.info(
            f"Caching result for key: {short_code} with value: {result_value} "
            f"in Redis"
        )
        # Keep cache TTL aligned with URL expiry so stale redirects auto-evict.
        if record.expires_at:
            ttl = max(0, int((record.expires_at - now).total_seconds()))
        else:
            ttl = None
        user_id = record.user_id
        mapping = {
            "user_id": user_id,
            "original_url": result_value,
            "expires_at": (
                record.expires_at.isoformat() if record.expires_at else None
            ),
            "last_accessed": now.isoformat(),
            "click_count": record.click_count,
            "is_active": int(record.is_active),
            "created_at": record.created_at.isoformat(),
            "is_disabled": int(record.is_disabled),
        }
        record.click_count += 1
        db.commit()
        CacheService.set_redirect_cache(
            short_code=short_code, mapping=mapping, ttl=ttl
        )
        logger.info(
            f"Result cached successfully for key: {short_code}."
            f"Returning value."
        )
        latency_ms = (time.perf_counter() - start) * 1000
        # Build the data for Analytics
        analytics_data = build_analytics_data(
            user_id=user_id,
            short_code=short_code,
            request=request,
            latency_ms=latency_ms,
            cache_hit=False,
        )
        threading.Thread(
            target=kafka_client_obj.publish_event,
            args=(TOPICS, short_code, analytics_data),
            daemon=True,
        ).start()
        RedirectResponse(url=result_value, status_code=status.HTTP_302_FOUND)
        return {"message": "Successful"}
    except (
        RecordNotFoundError,
        URLExpiredError,
        URLDeletedError,
        URLDisabledError,
        HTTPException,
    ):
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error during cache lookup for key: {short_code}. "
            f"Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
