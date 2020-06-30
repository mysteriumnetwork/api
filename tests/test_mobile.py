import json
from flask import jsonify

from tests.test_case import TestCase
from api.mobile import MIN_ANDROID_VERSION


class TestMobile(TestCase):
    def test_update_min_version(self):
        res = self._get('/v1/mobile/android/versions')
        self.assertEqual({'min_version': MIN_ANDROID_VERSION}, res.json)
