from sqlalchemy import text

from app.core.db import get_db
from app.core.db import redis_conn as redis_client
from app.core.logging import AppLogger

logger = AppLogger().get_logger()


def health_check():
    """Return a simple liveness response indicating the application is running."""
    logger.info("Application liveness check executed")
    return {"status": "I'm Up"}


def db_health_check():
    """Check connectivity to PostgreSQL and Redis, returning their individual statuses."""
    db_status = "down"
    redis_status = "down"
    #  Check PostgreSQL
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "up"
    except Exception as e:
        logger.warning(f"PostgreSQL health check failed: {e}")
        db_status = f"down: {str(e)}"
    finally:
        db.close()

    #  Check Redis
    try:
        if redis_client.ping():
            redis_status = "up"
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        redis_status = f"down: {str(e)}"

    logger.info(f"Health status postgres={db_status} redis={redis_status}")

    return {
        "postgres": db_status,
        "redis": redis_status,
        "status": (
            "ok" if db_status == "up" and redis_status == "up" else "degraded"
        ),
    }
