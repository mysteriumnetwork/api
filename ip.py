from geolite2 import geolite2


def detect_country(ip):
    reader = geolite2.reader()
    match = reader.get(ip)
    if match is None:
        return None
    return match['country']['iso_code']


def mask_ip_partially(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        raise ValueError('Incorrect ip address')
    anon_parts = parts[0:3] + ['X']
    return '.'.join(anon_parts)
