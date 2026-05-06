"""
Per-IP sliding-window rate limiter using slowapi + in-memory store.
For production with multiple workers, swap to a Redis backend.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/minute"],
)
