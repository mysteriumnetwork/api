import requests
from eth_keys import keys
import json
import base64


def print_payload_signature():
    pk = keys.PrivateKey(b'\x01' * 32)

    payload = {
        "service_proposal": {
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": "node1",
        }
    }

    signature = pk.sign_msg(json.dumps(payload))
    print json.dumps(payload)
    print pk.public_key.to_checksum_address().lower()
    print base64.b64encode(signature.to_bytes())


def test_signed_payload():
    payload = {
        "service_proposal": {
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": "node1",
        }
    }

    headers = {
        "identity": "0x1a642f0e3c3af545e7acbd38b07251b3990914f1",
        'signature': "Da1mAwK5abmXQCNsCE+YjsZbR9jTyEKqdrjxxMKwNzwr2NFnM35UiVQJWcg8rgL+X2PR60LoIUMlGU9OPaSoZwE="
    }

    re = requests.post(
        'http://127.0.0.1:5000/v1/signed_payload',
        data=json.dumps(payload),
        headers=headers
    )
    print re.content

test_signed_payload()