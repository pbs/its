import os
from io import BytesIO
from unittest import TestCase

from PIL import Image

from its.application import APP

from .test_pipeline import compare_pixels


class TestOverlay(TestCase):
    @classmethod
    def setUpClass(self):
        APP.config["TESTING"] = True
        self.client = APP.test_client()

    def test_simple_overlay(self):
        response = self.client.get(
            "tests/images/test.png?overlay=tests/images/five.png"
        )
        assert response.status_code == 200

    def test_overlay_with_leading_slash(self):
        response = self.client.get(
            "tests/images/test.png?overlay=/tests/images/five.png"
        )
        assert response.status_code == 200

    def test_simple_overlay_with_underscores(self):
        response = self.client.get(
            "tests/images/test.png?overlay=tests/images/five-something_with_underscores.png"
        )
        assert response.status_code == 200

    def test_empty_overlay(self):
        response = self.client.get("tests/images/test.png?overlay=")
        body = response.data.decode("utf-8")
        assert response.status_code == 400
        assert "no overlay image supplied" in body

    def test_legacy_passport_resize_overlay(self):
        response = self.client.get(
            "tests/images/test.png.resize.1000x1000.passport.png"
        )
        assert response.status_code == 200

    def test_legacy_passport_fit_overlay(self):
        response = self.client.get("tests/images/test.png.fit.1000x1000.passport.png")
        assert response.status_code == 200

    def test_overlay_image_resize_100_bytes(self):
        response = self.client.get(
            "tests/images/seagull.jpg.resize.100x100.passport.png"
        )
        expected_image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "images/expected/seagull.jpg.resize.100x100.passport.png",
        )

        comparison = compare_pixels(
            Image.open(expected_image_path), Image.open(BytesIO(response.data))
        )

        self.assertGreaterEqual(comparison, 0.99)

    def test_overlay_image_resize_500_bytes(self):
        response = self.client.get(
            "tests/images/seagull.jpg.resize.500x500.passport.png"
        )
        expected_image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "images/expected/seagull.jpg.resize.500x500.passport.png",
        )

        comparison = compare_pixels(
            Image.open(expected_image_path), Image.open(BytesIO(response.data))
        )

        self.assertGreaterEqual(comparison, 0.99)
