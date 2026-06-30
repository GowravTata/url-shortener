from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import TOPICS
from app.core.db import redis_conn as redis
from app.models.events import ClickArchive, ClickEvents
from app.models.url import URLModel
from app.models.user import Users
from app.services.kafka.admin import kafka_admin


def reset_environment(db: Session):
    """
    Completely reset the development environment.

    - Flush Redis
    - Truncate all PostgreSQL tables
    - Purge and recreate Kafka topic
    """

    try:
        # -----------------------------------------------------
        # Flush Redis
        # -----------------------------------------------------
        redis.flushdb()

        # -----------------------------------------------------
        # Truncate PostgreSQL
        # -----------------------------------------------------
        query = text(
            f"""
            TRUNCATE TABLE
                {ClickArchive.__tablename__},
                {ClickEvents.__tablename__},
                {URLModel.__tablename__},
                {Users.__tablename__}
            RESTART IDENTITY CASCADE;
            """
)

        db.execute(query)
        db.commit()

        # -----------------------------------------------------
        # Recreate Kafka Topic
        # -----------------------------------------------------
        response = kafka_admin.purge_topic(TOPICS)

        if not response["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response["error"],
            )

        return {
            "success": True,
            "message": "Environment reset successfully.",
            "database": "All tables truncated.",
            "redis": "Redis cache flushed.",
            "kafka": f"Topic '{TOPICS}' recreated.",
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )