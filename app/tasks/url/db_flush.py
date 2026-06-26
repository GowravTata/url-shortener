from datetime import datetime, timezone

from app.core.celery_app import celery_app
from app.core.db import get_db
from app.core.db import redis_conn as redis
from app.core.logging import AppLogger
from app.models.url import URLModel


@celery_app.task
def flush_db():
    """Utility function to sync the click count from Redis to the database"""
    try:
        db = next(get_db())
        logger = AppLogger().get_logger()
        logger.info("Starting database flush to sync click counts.")

        updated_records = 0

        for key in redis.scan_iter(match="url:*"):
            try:
                short_code = key.split(":")[1]

                pipe = redis.pipeline()
                pipe.hget(key, "click_count")
                pipe.hget(key, "last_accessed")
                pipe.hset(key, "click_count", 0)
                click_count, last_accessed, _ = pipe.execute()

                if click_count is None and last_accessed is None:
                    logger.info(
                        f"No click count or last accessed found for key: {key}"
                    )
                    continue

                # Redis hashes store strings; coerce click_count safely to int.
                try:
                    click_count = int(click_count) if click_count else 0
                except Exception:
                    logger.warning(
                        f"Invalid click_count for {short_code}: {click_count}"
                    )
                    click_count = 0

                # Parse last_accessed and normalize timezone for DB comparisons.
                parsed_last_accessed = None
                if last_accessed:
                    try:
                        parsed_last_accessed = datetime.fromisoformat(
                            last_accessed
                        )
                        if parsed_last_accessed.tzinfo is None:
                            parsed_last_accessed = parsed_last_accessed.replace(
                                tzinfo=timezone.utc
                            )
                    except Exception:
                        logger.warning(
                            f"Invalid last_accessed for {short_code}: {last_accessed}"
                        )

                # Fetch matching DB row for this short code.
                record = (
                    db.query(URLModel)
                    .filter(URLModel.short_code == short_code)
                    .first()
                )

                if not record:
                    logger.warning(
                        f"No DB record found for short_code={short_code}"
                    )
                    continue

                # Apply additive click updates and monotonic timestamp updates.
                if click_count > 0:
                    record.click_count += click_count

                if parsed_last_accessed:
                    if (
                        not record.last_accessed
                        or parsed_last_accessed > record.last_accessed
                    ):
                        record.last_accessed = parsed_last_accessed

                updated_records += 1

            except Exception as e:
                logger.exception(f"Error processing key={key}: {str(e)}")

        db.commit()

        logger.info(
            f"Flush completed successfully. Updated {updated_records} records."
        )

        return {
            "message": "Flushed Redis data to DB successfully",
            "updated_records": updated_records,
        }

    except Exception as e:
        db.rollback()
        logger.exception(f"Flush failed: {str(e)}")
        raise
