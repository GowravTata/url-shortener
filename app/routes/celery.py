from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.logging import AppLogger
from app.services.url.cleanup import deactivate_expired_urls

celery_router = APIRouter(tags=["Celery"])
logger = AppLogger().get_logger()


@celery_router.post(
    "/cleanup",
    summary="Deleted Expired URLs from Redis & DB",
    description="Deletes Expired URLS from Redis & DB",
)
async def clean_up_expired_urls(db: Session = Depends(get_db)) -> Dict:
    """Manually trigger deletion of expired and inactive URLs from Redis and the database."""
    logger.info("Manual cleanup endpoint invoked")
    return deactivate_expired_urls(db=db)
