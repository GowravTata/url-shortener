from app.core.config import (ANALYTICS, DELETED, GEO, PATCHING, URL,
                             USER_AGENT, USER_URLS)


class CacheKeys:

    @staticmethod
    def redirect(short_code: str) -> str:
        """Redis hash key for redirect payload and click counters."""
        return f"{URL}:{short_code}"

    @staticmethod
    def analytics(short_code: str) -> str:
        """Redis key for short-lived analytics response caching."""
        return f"{ANALYTICS}:{short_code}"

    @staticmethod
    def patching(short_code: str) -> str:
        """Redis key used as a temporary lock during patch operations."""
        return f"{PATCHING}:{short_code}"

    @staticmethod
    def deleted(short_code: str) -> str:
        """Redis key used to mark deletion in progress and block stale reads."""
        return f"{DELETED}:{short_code}"

    @staticmethod
    def user_urls(user_id: int) -> str:
        """Redis key namespace for user-specific URL listing caches."""
        return f"{USER_URLS}:{user_id}"

    @staticmethod
    def geo_ip(ip_address: str) -> str:
        """Redis key namespace for Geo IP Address details"""
        return f"{GEO}:{ip_address}"

    @staticmethod
    def user_agent(user_agent: str) -> str:
        """Redis key namespace for User Agent details"""
        return f"{USER_AGENT}:{user_agent}"
