import models


def shorten_node_key(node_key):
    if node_key and len(node_key) == models.IDENTITY_LENGTH_LIMIT:
        return node_key[:6] + '..' + node_key[-4:]
    else:
        return node_key
