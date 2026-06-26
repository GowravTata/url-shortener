from datetime import datetime


def serialize_url_for_cache(source):
    """Convert a URL ORM model into a Redis hash-compatible dictionary."""
    return {
        "user_id": source.user_id,
        "original_url": source.original_url,
        "expires_at": (
            source.expires_at.isoformat() if source.expires_at else None
        ),
        "is_active": int(source.is_active),
        "is_disabled": int(source.is_disabled),
        "created_at": source.created_at.isoformat(),
        "click_count": source.click_count,
        "last_accessed": (
            source.last_accessed.isoformat() if source.last_accessed else ""
        ),
    }


def serialize_url_metadata_response(source):
    """Build lightweight metadata response by dropping internal/cache-only fields."""
    exclude = {"is_disabled", "expires_at", "click_count"}
    # Keep response payload focused on fields needed by info endpoints.
    metadata = {k: v for k, v in source.items() if k not in exclude}
    return metadata


def normalize_data(payload: dict):
    for key in payload.keys():
        value = payload[key]
        if value is not None and not isinstance(value, (str, int, float, bool)):
            payload[key] = str(value)
    return payload


def formatted_time():
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted
