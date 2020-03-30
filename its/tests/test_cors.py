import unittest
from unittest import TestCase

from its.application import APP


class TestCorsHeaders(TestCase):
    @classmethod
    def setUpClass(self):
        APP.config["TESTING"] = True
        self.client = APP.test_client()

    def test_cors_on_get(self):
        resp = self.client.get(
            "tests/images/test.png", headers=[["Origin", "www.example.com"]]
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "www.example.com"

        resp = self.client.get(
            "tests/images/test.png", headers=[["Origin", "another.example.com"]]
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "another.example.com"

        resp = self.client.get(
            "tests/images/test.png", headers=[["Origin", "evil.example.com"]]
        )
        assert resp.headers.get("Access-Control-Allow-Origin") is None

    def test_cors_on_options(self):
        resp = self.client.options(
            "tests/images/test.png", headers=[["Origin", "www.example.com"]]
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "www.example.com"

        resp = self.client.options(
            "tests/images/test.png", headers=[["Origin", "another.example.com"]]
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "another.example.com"

        resp = self.client.options(
            "tests/images/test.png", headers=[["Origin", "evil.example.com"]]
        )
        assert resp.headers.get("Access-Control-Allow-Origin") is None


if __name__ == "__main__":
    unittest.main()
