from eth_keys import keys


def sign_message_with_static_key(message):
    pk = keys.PrivateKey(b'\x01' * 32)
    signature = pk.sign_msg(message)
    signature_bytes = signature.to_bytes()
    public_address = pk.public_key.to_checksum_address()
    return signature_bytes, public_address