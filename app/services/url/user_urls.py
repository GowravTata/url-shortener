import math

from sqlalchemy.orm import Session

from app.core.logging import AppLogger
from app.utils.url_repository import get_urls_by_user

logger = AppLogger().get_logger()


def get_all_urls(
    user_id: int,
    db: Session,
    page: int,
    limit: int,
    order: str = "desc",
    search: str | None = None,
):
    try:
        logger.info(f"Fetching URLs for user_id={user_id}")

        records, total = get_urls_by_user(
            db=db,
            user_id=user_id,
            page=page,
            limit=limit,
            search=search,
            order=order,
        )

        # Keep payload minimal for list view; detail view is served elsewhere.
        all_records = [
            {
                "id": record.id,
                "short_code": record.short_code,
                "original_url": record.original_url,
                "created_at": record.created_at,
                "click_count": record.click_count,
            }
            for record in records
        ]

        return {
            "urls": all_records,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                # Compute page count server-side so clients do not replicate logic.
                "pages": math.ceil(total / limit),
            },
        }

    except Exception as e:
        logger.exception(f"Error fetching URLs for user_id={user_id}")
        raise e
