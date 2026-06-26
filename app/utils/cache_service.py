import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from app.core.config import GEO_IP_TTL
from app.core.db import redis_conn as redis
from app.utils.cache_keys import CacheKeys


def chunked(data, size):
    for i in range(0, len(data), size):
        yield data[i : i + size]


class CacheService:
    """Centralized Redis access layer for URL data, analytics, and control flags."""

    def __init__(self):
        self.acquired_locks: List[Tuple[str, str]] = []

    # GET Operations
    @staticmethod
    def get_redirect_cache(short_code: str) -> Dict | None:
        key = CacheKeys.redirect(short_code)
        cached = redis.hgetall(key)
        if not cached:
            return None
        return cached

    @staticmethod
    def get_analytics_cache(short_code: str):
        key = CacheKeys.analytics(short_code)
        cached = redis.get(key)
        if not cached:
            return None
        return json.loads(cached)

    @staticmethod
    def is_deleted_flag(short_code: str):
        return redis.get(CacheKeys.deleted(short_code=short_code))

    @staticmethod
    def is_patching_flag(short_code: str):
        return redis.get(CacheKeys.patching(short_code=short_code))

    @staticmethod
    def get_patching_flags_bulk(short_codes: List[str]):
        keys = [CacheKeys.patching(short_code=code) for code in short_codes]
        return redis.mget(keys=keys)

    @staticmethod
    def get_delete_flags_bulk(short_codes: List[str]):
        keys = [CacheKeys.patching(short_code=code) for code in short_codes]
        return redis.mget(keys=keys)

    # Set/Update

    @staticmethod
    def set_redirect_cache(short_code, mapping, ttl: int | None = None) -> None:
        key = CacheKeys.redirect(short_code)
        pipe = redis.pipeline()
        pipe.hset(key, mapping=mapping)
        if ttl and ttl > 0:
            pipe.expire(key, ttl)
        pipe.execute()

    @staticmethod
    def set_analytics_cache(short_code, ttl, response):
        analytics_key = CacheKeys.analytics(short_code)
        json_response = json.dumps(response)
        redis.setex(analytics_key, ttl, json_response)

    # Invalidation Operations

    @staticmethod
    def invalidate_redirect_cache(short_code: str):
        redis.delete(CacheKeys.redirect(short_code))

    @staticmethod
    def invalidate_analytics_cache(short_code: str):
        redis.delete(CacheKeys.analytics(short_code))

    @staticmethod
    def invalidate_deleted_flag_cache(short_code):
        redis.delete(CacheKeys.deleted(short_code))

    @staticmethod
    def invalidate_all_url_cache(short_code):
        CacheService.invalidate_redirect_cache(short_code)
        CacheService.invalidate_analytics_cache(short_code)

    @staticmethod
    def invalidate_short_codes_bulk(short_codes: list):
        pipe = redis.pipeline()
        for short_code in short_codes:
            pipe.delete(CacheKeys.redirect(short_code))
        pipe.execute()

    @staticmethod
    def invalidate_redirect_cache_bulk(short_codes):
        keys = [f"url:{short_code}" for short_code in short_codes]
        if keys:
            redis.delete(*keys)

    # Patch Locks

    @staticmethod
    def acquire_patch_lock(short_code: str):
        key = CacheKeys.patching(short_code=short_code)
        token = str(uuid.uuid4())
        acquired = redis.set(key, token, nx=True, ex=3600)
        return token if acquired else None

    @staticmethod
    def acquire_patch_lock_bulk(short_codes):
        acquired = []
        locked = []
        pipe = redis.pipeline()
        tokens = {}

        short_codes = list(short_codes)
        for short_code in short_codes:
            token = str(uuid.uuid4())
            tokens[short_code] = token
            pipe.set(CacheKeys.patching(short_code), token, nx=True, ex=30)

        results = pipe.execute()

        for short_code, result in zip(short_codes, results):
            if result:
                acquired.append((short_code, tokens[short_code]))
            else:
                locked.append(short_code)

        return acquired, locked

    @staticmethod
    def release_patch_lock(short_code: str, token: str):
        key = CacheKeys.patching(short_code=short_code)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1]
        then return redis.call("del", KEYS[1])
        else return 0
        end
        """
        return redis.eval(lua_script, 1, key, token)

    # Delete Locks

    @staticmethod
    def acquire_delete_lock(short_code: str):
        key = CacheKeys.deleted(short_code=short_code)
        token = str(uuid.uuid4())
        acquired = redis.set(key, token, nx=True, ex=60)
        return token if acquired else None

    @staticmethod
    def acquire_delete_lock_bulk(short_codes: list):
        BATCH_SIZE = 5000
        acquired = []
        failed = []
        tokens = {}

        for batch in chunked(short_codes, BATCH_SIZE):
            pipe = redis.pipeline()

            for short_code in batch:
                token = str(uuid.uuid4())
                tokens[short_code] = token
                pipe.set(CacheKeys.deleted(short_code), token, nx=True, ex=15)

            results = pipe.execute()

            for code, success in zip(batch, results):  # ✅ fixed bug
                if success:
                    acquired.append((code, tokens[code]))
                else:
                    failed.append(code)

        return acquired, failed

    @staticmethod
    def release_delete_lock(short_code: str, token: str):
        key = CacheKeys.deleted(short_code=short_code)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1]
        then return redis.call("del", KEYS[1])
        else return 0
        end
        """
        return redis.eval(lua_script, 1, key, token)

    # Bulk Release

    def release_delete_lock_bulk(self):
        keys = [
            CacheKeys.deleted(short_code=code[0])
            for code in self.acquired_locks
        ]
        if keys:
            redis.delete(*keys)
        self.acquired_locks.clear()

    def release_patch_lock_bulk(self):
        keys = [
            CacheKeys.patching(short_code=code[0])
            for code in self.acquired_locks
        ]
        if keys:
            redis.delete(*keys)
        self.acquired_locks.clear()

    def release_all(self):
        for code, token in self.acquired_locks:
            try:
                CacheService.release_delete_lock(code, token)
            except Exception:
                pass
        self.acquired_locks.clear()

    @staticmethod
    def get_geo_ip_address(ip_address):
        key = CacheKeys.geo_ip(ip_address)
        cached = redis.hgetall(key)
        if not cached:
            return None
        return cached

    @staticmethod
    def set_geo_ip_address(ip_address, mapping, ttl=GEO_IP_TTL):
        ip_address_key = CacheKeys.geo_ip(ip_address)
        pipe = redis.pipeline()
        pipe.hset(ip_address_key, mapping=mapping)
        pipe.expire(ip_address_key, ttl)
        pipe.execute()

    @staticmethod
    def get_user_agent(user_agent):
        user_agent_key = CacheKeys.user_agent(user_agent)
        cached = redis.hgetall(user_agent_key)
        if not cached:
            return None
        return cached

    @staticmethod
    def set_user_agent(user_agent, mapping, ttl=GEO_IP_TTL):
        user_agent_key = CacheKeys.user_agent(user_agent)
        pipe = redis.pipeline()
        pipe.hset(user_agent_key, mapping=mapping)
        pipe.expire(user_agent_key, ttl)
        pipe.execute()
