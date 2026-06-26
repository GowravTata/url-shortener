from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.logging import AppLogger
from app.models.url import URLModel


def get_url_by_short_code(
    short_code: str,
    db: Session,
    user_id: Optional[int] = None,
    include_deleted: bool = False,
) -> Optional[URLModel]:
    """Fetch a URL record by its short code.
    Optionally filter by user_id if provided."""
    logger = AppLogger().get_logger()

    try:
        search_filter = {"short_code": short_code, "is_active": True}
        if include_deleted:
            search_filter.pop("is_active")
        logger.info(
            f"Querying DB for short_code={short_code}, user_id={user_id}"
        )

        query = db.query(URLModel).filter_by(**search_filter)

        # Apply user filter only if provided
        if user_id is not None:
            query = query.filter(URLModel.user_id == user_id)

        return query.first()

    except Exception as e:
        logger.exception(
            f"Error querying DB for short_code={short_code}, user_id={user_id}."
            f"Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def get_urls_by_user(
    db: Session,
    user_id: int,
    page: int,
    limit: int,
    search: str | None = None,
    order: str = "desc",
):
    """Return paginated URLs for a user with optional text search and sort order."""
    query = db.query(URLModel).filter(URLModel.user_id == user_id)
    if search:
        # Search over both original URL and short code to support list filtering.
        query = query.filter(
            or_(
                URLModel.original_url.ilike(f"%{search}%"),
                URLModel.short_code.ilike(f"%{search}%"),
            )
        )
    if order == "asc":
        query = query.order_by(URLModel.created_at.asc())
    else:
        query = query.order_by(URLModel.created_at.desc())
    total = query.count()
    offset = (page - 1) * limit
    records = query.offset(offset).limit(limit).all()
    return records, total
