"""Per-scope API rate-limit definitions used by the Redis limiter."""

RATE_LIMITS = {
    "redirect": {"limit": 1000000000, "window": 60},
    "create": {"limit": 1000000000, "window": 60},
    "info": {"limit": 60, "window": 60},
    "analytics": {"limit": 60, "window": 60},
    "patch": {"limit": 15, "window": 60},
    "delete": {"limit": 10, "window": 60},
    "login": {"limit": 5, "window": 60},
    "signup": {"limit": 3, "window": 60},
    "userinfo": {"limit": 10, "window": 60},
    "restore": {"limit": 10, "window": 60},
}
