from flask import jsonify


MIN_ANDROID_VERSION = "0.39.4"


def register_endpoints(app):
    @app.route('/v1/mobile/android/versions', methods=['GET'])
    def min_version():
        return jsonify({
            'min_version': MIN_ANDROID_VERSION
        })
