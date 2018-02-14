from geoip import geolite2


def detect_country(ip):
    match = geolite2.lookup(ip)
    if match is None:
        return None
    return match.country


def mask_ip_partially(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        raise ValueError('Incorrect ip address')
    anon_parts = parts[0:3] + ['X']
    return '.'.join(anon_parts)
