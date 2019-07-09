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


def register_endpoints(app):
    # End Point which creates an affiliate record
    @app.route('/v1/affiliates', methods=['POST'])
    @validate_json
    def create_affiliate():
        payload = request.get_json(force=True)

        email = payload.get('email', None)
        referral_code = payload.get('referral_code', None)
        if referral_code:
            referral_code = referral_code.strip()

        payout_eth_address = payload.get('payout_eth_address', None)

        if email is None:
            return jsonify(field='email', message='Email is required'), 400

        if not validate_email_address(email):
            return jsonify(field='email', message='Email is invalid'), 400

        if payout_eth_address is None:
            return jsonify(
                field='payout_eth_address',
                message='Payout address is required'
            ), 400

        if not is_valid_eth_address(payout_eth_address):
            return jsonify(
                field='payout_eth_address',
                message='Payout address is not a valid Ethereum address'
            ), 400

        if not referral_code:
            referral_code = generate_referral_code(email)

        record = Affiliate.query.filter_by(email=email).first()
        if record:
            return jsonify(field='email', message='Email already exists'), 400

        if record is None:
            new_record = Affiliate(
                email,
                payout_eth_address,
                referral_code
            )
            db.session.add(new_record)
            db.session.commit()

        return jsonify(
            message="Successfully registered your referral code.",
            referral_code=referral_code
        )
