import binascii
from functools import wraps
import json
from flask import request, jsonify
import settings
import base64
from signature import (
    recover_public_address,
    ValidationError as SignatureValidationError
)


def is_json_dict(data):
    try:
        json_data = json.loads(data)
    except ValueError:
        return False
    if not isinstance(json_data, dict):
        return False
    return True


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        if not is_json_dict(request.data):
            return jsonify({"error": 'payload must be a valid json'}), 400
        return f(*args, **kw)
    return wrapper


def restrict_by_ip(f):
    @wraps(f)
    def wrapper(*args, **kw):
        if settings.RESTRICT_BY_IP_ENABLED:
            if request.remote_addr not in settings.ALLOWED_IP_ADDRESSES:
                return jsonify(error='resource is forbidden'), 403

        return f(*args, **kw)

    return wrapper


def recover_identity(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            caller_identity = decode_authorization_header(request.headers)
        except ValueError as err:
            return jsonify(error=str(err)), 401

        kw['caller_identity'] = caller_identity
        return f(*args, **kw)

    return wrapper


def decode_authorization_header(headers):
    # Authorization request header format:
    # Authorization: Signature <signature_base64_encoded>
    authorization = headers.get('Authorization')
    if not authorization:
        raise ValueError('missing Authorization in request header')

    authorization_parts = authorization.split(' ')
    if len(authorization_parts) != 2:
        raise ValueError('invalid Authorization header value provided, correct'
                         ' format: Signature <signature_base64_encoded>')

    authentication_type, signature_base64_encoded = authorization_parts

    if authentication_type != 'Signature':
        raise ValueError('authentication type have to be Signature')

    if signature_base64_encoded == '':
        raise ValueError('signature was not provided')

    try:
        signature_bytes = base64.b64decode(signature_base64_encoded)
    except binascii.Error as err:
        raise ValueError('signature must be base64 encoded: {0}'.format(err))

    try:
        return recover_public_address(
            request.data,
            signature_bytes,
        ).lower()
    except SignatureValidationError as err:
        raise ValueError('invalid signature format: {0}'.format(err))
