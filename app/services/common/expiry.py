from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status


def get_expiry_date(expiry: datetime = None) -> Optional[datetime]:
    """Convert an optional expiry datetime to UTC; defaults to 30 days from now if not provided."""
    try:
        if expiry:
            # Normalize any incoming datetime to timezone-aware UTC.
            expiry_dt = expiry
            if not isinstance(expiry, datetime):
                expiry_dt = datetime.fromisoformat(expiry)
            if expiry_dt is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            else:
                expiry_dt = expiry_dt.astimezone(timezone.utc)

        else:
            # Product default for links without explicit expiry.
            expiry_dt = datetime.now(timezone.utc) + timedelta(hours=2)

        now = datetime.now(timezone.utc)

        if expiry_dt < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expiry cannot be in the past",
            )

        return expiry_dt

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS",
        )
