from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import ANALYTICS, IP
from app.core.db import get_db
from app.core.dependencies import get_current_user_id, rate_limit_dependency
from app.core.logging import AppLogger
from app.services.url.analytics import get_short_code_analytics
from app.services.url.dashboard import dashboard_analytics

analytics_router = APIRouter(tags=["Analytics"], prefix="/v1/analytics")
logger = AppLogger().get_logger()


@analytics_router.get(
    "/{short_code}/analytics",
    summary="Get Short URL Analytics",
    description="Retrieve analytics data for a given short URL, including "
    "click count and timestamps of clicks",
    dependencies=[rate_limit_dependency(scope=ANALYTICS, identifier_type=IP)],
)
async def get_analytics(
    short_code: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Dict:
    """Return click analytics (total clicks, last accessed timestamp) for a short URL."""
    logger.info(
        f"Analytics request for user_id={user_id} " f"short_code={short_code}"
    )
    return get_short_code_analytics(
        short_code=short_code, user_id=user_id, db=db
    )


@analytics_router.get(
    "/analytics/dashboard",
    summary="API to Provide Analytics Dashboard",
)
async def analytics_dashboard(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    logger.info("Starting Getting Dashboard Analytics")
    return dashboard_analytics(user_id=user_id,db=db)
