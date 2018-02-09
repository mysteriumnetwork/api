from geoip import geolite2


def detect_country(ip):
    match = geolite2.lookup(ip)
    if match is None:
        return None
    return match.country
