from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options


cache_opts = {
    'cache.type': 'memory',
}

cache = CacheManager(**parse_cache_config_options(cache_opts))
sessionStatCallCache = cache.get_cache('sessionStatsCallCache', expire=45)
proposalPingCallCache = cache.get_cache('propsalPingCallCache', expire=45)


def isSessionStatRecentlyCalled(session_key):
    try:
        sessionStatCallCache.get(key=session_key)
        return True
    except KeyError:
        return False


def markSessionStatRecentlyCalled(session_key):
    sessionStatCallCache.put(session_key, True)


def isProposalPingRecentlyCalled(node_key, service_type):
    try:
        k = node_key + service_type
        proposalPingCallCache.get(key=k)
        return True
    except KeyError:
        return False


def markProposalPingRecentlyCalled(node_key, service_type):
    k = node_key + service_type
    proposalPingCallCache.put(k, True)
