"""Redis-backed request throttling utilities."""

from fastapi import HTTPException, status

from app.core.db import redis_conn as redis
from app.core.logging import AppLogger
from app.core.rate_limits import RATE_LIMITS

logger = AppLogger().get_logger()


def check_rate_limit(scope: str, identifier: str) -> bool:
    """Enforce per-scope rate limits for a caller identifier."""

    try:
        limit = RATE_LIMITS.get(scope).get("limit")
        window = RATE_LIMITS.get(scope).get("window")
        redis_key = f"rate:{scope}:{identifier}"
        current_count = redis.incr(redis_key)
        if current_count == 1:
            redis.expire(redis_key, window)

        logger.info(
            f"[RATE LIMIT] key={redis_key} "
            f"count={current_count}/{limit}")

        if current_count > limit:
            logger.warning(f"[RATE LIMIT EXCEEDED] key={redis_key}")

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded. "
                    f"Max {limit} requests in {window} seconds."
                ),
            )
        return True

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(
            f"Rate limiter failure for key={scope}:{identifier}: {e}"
        )
        return True
