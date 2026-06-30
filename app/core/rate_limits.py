"""Per-scope API rate-limit definitions used by the Redis limiter."""

RATE_LIMITS = {
    "redirect": {"limit": 1000000000, "window": 60},
    "create": {"limit": 1000000000, "window": 60},
    "info": {"limit": 1000000000, "window": 60},
    "analytics": {"limit": 1000000000, "window": 60},
    "patch": {"limit": 1000000000, "window": 60},
    "delete": {"limit": 1000000000, "window": 60},
    "login": {"limit": 1000000000, "window": 60},
    "signup": {"limit": 1000000000, "window": 60},
    "userinfo": {"limit": 1000000000, "window": 60},
    "restore": {"limit": 1000000000, "window": 60},
}