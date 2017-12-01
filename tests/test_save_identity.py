import requests
import json

def test_save_identity():
    payload = {
        'identity': '0x0000000000000000000000000000000000000001',
    }

    re = requests.post(
        'http://127.0.0.1:5000/v1/save_identity',
        data=json.dumps(payload)
    )
    print re.content


test_save_identity()