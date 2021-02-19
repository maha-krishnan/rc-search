from r2essentials.config import get_from_env

class Config(object):
    REDIS_HOST = get_from_env("REDIS_HOST", "localhost")
    REDIS_PORT = get_from_env("REDIS_PORT", "6379")
    REDIS_DB = get_from_env("REDIS_DB", "0")
    REDIS_PASSWORD = get_from_env("REDIS_PASSWORD", None)
    REDIS_SOCKET_TIMEOUT = get_from_env("REDIS_SOCKET_TIMEOuT", None)


def cache_session():
    """Opens cache sessions and returns handle"""
    from lib.cache import Cache
    cache = Cache(host=Config.REDIS_HOST, port=Config.REDIS_PORT,
                  db=Config.REDIS_DB, password=Config.REDIS_PASSWORD,
                  socket_timeout=Config.REDIS_SOCKET_TIMEOUT)
    return cache
