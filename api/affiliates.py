from random import randint

from email_validator import validate_email, EmailNotValidError
from eth_utils.address import is_hex_address as is_valid_eth_address
from flask import request, jsonify

from models import db, Affiliate
from request_helpers import validate_json


def validate_email_address(email):
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return False
    return True


def generate_referral_code(email):
    name = ''.join(email[:2]).upper()
    while True:
        code = name + "RPI" + str(randint(100, 999))
        record = Affiliate.query.filter_by(referral_code=code).first()
        if not record:
            break

    return code


def referral_code_exists(referral_code):
    return Affiliate.query.filter_by(referral_code=referral_code).first()


def validate_fields(email, payout_eth_address, referral_code):
    if email is None:
        return jsonify(field='email', message='Email is required')

    if not validate_email_address(email):
        return jsonify(field='email', message='Email is invalid')

    if payout_eth_address is None:
        return jsonify(
            field='payout_eth_address',
            message='Payout address is required'
        )

    if not is_valid_eth_address(payout_eth_address):
        return jsonify(
            field='payout_eth_address',
            message='Payout address is not a valid Ethereum address'
        )

    if referral_code:
        if len(referral_code) > 20:
            return jsonify(field='referral_code', message='Referral code should not exceed 20 characters')
        if len(referral_code) < 6:
            return jsonify(field='referral_code', message='Referral code should be at least 6 characters')
        if referral_code_exists(referral_code):
            return jsonify(field='referral_code', message='This referral code already exists')

    record = Affiliate.query.filter_by(email=email).first()
    if record:
        return jsonify(field='email', message='Email already exists')

    return None


def register_endpoints(app):
    # End Point which creates an affiliate record
    @app.route('/v1/affiliates', methods=['POST'])
    @validate_json
    def create_affiliate():
        payload = request.get_json(force=True)

        email = payload.get('email', '').strip()
        payout_eth_address = payload.get('payout_eth_address', '').strip()
        referral_code = payload.get('referral_code', '').strip()

        validation_error = validate_fields(email, payout_eth_address, referral_code)
        if validation_error is not None:
            return validation_error, 400

        if not referral_code:
            referral_code = generate_referral_code(email)

        record = Affiliate(
            email,
            payout_eth_address,
            referral_code
        )
        db.session.add(record)
        db.session.commit()

        return jsonify(
            message="Successfully registered your referral code.",
            referral_code=referral_code
        )
