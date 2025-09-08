from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend

from config import CACHE_BACKEND, REDIS_URL

def init_cache(app):
    """
    Initialize cache backend.
    - CACHE_BACKEND == "memory" -> in-memory backend
    - CACHE_BACKEND == "redis"  -> redis backend (requires aioredis package)
    """
    if CACHE_BACKEND == "redis":
        FastAPICache.init(RedisBackend(REDIS_URL), prefix="fastapi-cache")
    else:
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
