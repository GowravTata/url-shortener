from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import IP, REDIRECT
from app.core.db import get_db
from app.core.dependencies import rate_limit_dependency
from app.core.logging import AppLogger
from app.services.url.redirect import get_original_url

redirect_router = APIRouter(tags=["Redirect"])
logger = AppLogger().get_logger()


@redirect_router.get(
    "/{short_code}",
    summary="Get Orignal URL",
    description="Retrieve the Orignal URL for a given short URL if it "
    "exists",
    dependencies=[rate_limit_dependency(scope=REDIRECT, identifier_type=IP)],
)
async def gets_original_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Redirect the caller to the original URL mapped to the given short code."""
    logger.info(f"Redirect lookup for short_code={short_code}")
    return get_original_url(short_code=short_code, db=db, request=request)
