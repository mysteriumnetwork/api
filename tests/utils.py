from eth_keys import keys
import base64


def sign_message_with_static_key(message):
    pk = keys.PrivateKey(b'\x01' * 32)
    signature = pk.sign_msg(message)
    signature_bytes = signature.to_bytes()
    public_address = pk.public_key.to_checksum_address()
    return signature_bytes, public_address

def generate_test_authorization(message=''):
    signature, public_address = sign_message_with_static_key(message)
    headers = {
        "Authorization": "Signature {}".format(base64.b64encode(signature))
    }

    return {
        'headers': headers,
        'public_address': public_address.lower()
    }
