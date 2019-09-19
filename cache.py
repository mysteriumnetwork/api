from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options


cache_opts = {
    'cache.type': 'memory',
}

cache = CacheManager(**parse_cache_config_options(cache_opts))
sessionStatCallCache = cache.get_cache('sessionStatsCallCache', expire=45)


def recentlyCalled(session_key):
    try:
        sessionStatCallCache.get(key=session_key)
        return True
    except KeyError:
        return False


def markRecentlyCalled(session_key):
    sessionStatCallCache.put(session_key, True)
