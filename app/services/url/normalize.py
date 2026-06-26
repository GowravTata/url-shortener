# app/services/url/normalize.py

from datetime import datetime, timezone


def normalize_cache_data(source: dict) -> dict:
    """Normalise raw Redis hash data into Python-typed fields (int, bool, datetime)."""

    def _decode(v):
        return v.decode() if isinstance(v, bytes) else v

    def _int(v, default=0):
        try:
            return int(_decode(v))
        except BaseException:
            return default

    def _bool(v, default=0):
        return bool(_int(v, default))

    def _dt(v):
        v = _decode(v)
        if not v:
            return None
        try:
            # Redis stores strings; normalize to timezone-aware datetime when possible.
            dt = datetime.fromisoformat(v)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except BaseException:
            return None

    return {
        "user_id": _int(source.get("user_id")),
        "original_url": _decode(source.get("original_url")),
        "is_active": _bool(source.get("is_active"), 1),
        "is_disabled": _bool(source.get("is_disabled"), 0),
        "click_count": _int(source.get("click_count")),
        "last_accessed": _dt(source.get("last_accessed")),
        "expires_at": _dt(source.get("expires_at")),
        "created_at": _dt(source.get("created_at")),
    }
