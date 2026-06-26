from fastapi import APIRouter

from app.core.logging import AppLogger
from app.services.health.database_cache import db_health_check, health_check

health_check_router = APIRouter(
    tags=["Health Check"],
    prefix="/v1/health",
)
logger = AppLogger().get_logger()


@health_check_router.get(
    "/database_healthcheck",
    summary="Check Health of Database",
    description="API to get the health of database & cache",
)
async def application_health_checker() -> dict:
    """Check the health of the PostgreSQL database and Redis cache."""
    logger.info("Database health endpoint invoked")
    return db_health_check()


@health_check_router.get(
    "/application",
    summary="Check Health of Application",
    description="API to get the health of Application",
)
async def application_health_check() -> dict:
    """Return a simple liveness response for the application."""
    logger.info("Application health endpoint invoked")
    return health_check()
