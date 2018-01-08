from eth_keys.datatypes import Signature
from eth_keys.exceptions import ValidationError
from eth_keys.utils.address import public_key_bytes_to_address
from eth_utils import to_checksum_address


def recover_public_key(message, signature_bytes):
    signature = Signature(signature_bytes)
    public_key = signature.recover_public_key_from_msg(message)
    return public_key


def recover_public_address(message, signature_bytes):
    public_key = recover_public_key(message, signature_bytes)
    public_address = to_checksum_address(
        public_key_bytes_to_address(public_key.to_bytes())
    )
    return public_address
