import os
import random
import string
import logging


def generate_random_string():
    N = 10
    # + string.ascii_uppercase
    return ''.join(random_character() for _ in range(N))


def random_character():
    return random.SystemRandom().choice(string.ascii_lowercase + string.digits)


def get_app_path():
    return os.path.dirname(os.path.realpath(__file__))


def setup_logger():
    # setup logger
    log_format = '%(asctime)s %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(
        filename='{}/api.log'.format(get_app_path()),
        level=logging.DEBUG,
        format=log_format,
        datefmt=log_datefmt
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
    logging.getLogger('').addHandler(console)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_node_type_from_proposal(proposal):
    service_definition = proposal.get('service_definition', None)
    if not service_definition:
        return None

    if not isinstance(service_definition, dict):
        return None

    location = service_definition.get('location', None)
    if not location:
        return None

    return location.get("node_type", None)
