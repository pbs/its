from unittest import TestCase

from its.application import APP


class TestClientErrorHandling(TestCase):
    @classmethod
    def setUpClass(self):
        APP.config["TESTING"] = True
        self.client = APP.test_client()

    def test_invalid_namespace(self):
        response = self.client.get("/invalid-namespace/image.jpg")
        body = response.data.decode("utf-8")
        assert response.status_code == 400
        assert "invalid-namespace is not a configured namespace" in body

    def test_fit_synonyms(self):
        response = self.client.get("tests/images/test.jpeg?fit=10x10&crop=20x20")
        assert response.status_code == 400
        assert (
            "use only one of these synonyms: fit, crop, focalcrop"
            in response.data.decode("utf-8")
        )

    def test_non_image_file(self):
        response = self.client.get("/tests/images/not-an-image.jpg")
        body = response.data.decode("utf-8")
        assert response.status_code == 400
        assert "tests/images/not-an-image.jpg is not an image file" in body

    def test_large_image_file(self):
        response = self.client.get("/tests/images/large.jpg")
        body = response.data.decode("utf-8")
        assert response.status_code == 400
        assert "tests/images/large.jpg  is too large. Please use a smaller one" in body

    def test_no_cache_headers_on_400(self):
        response = self.client.get("/tests/images/not-an-image.jpg")
        assert response.status_code == 400
        assert "Cache-Control" not in response.headers.keys()

    def test_gif_source_file(self):
        response = self.client.get("/tests/images/secretly-a-gif.jpg")
        body = response.data.decode("utf-8")
        assert response.status_code == 400
        assert "tests/images/secretly-a-gif.jpg is not a supported file type" in body

    def test_gif_source_file_with_transforms(self):
        response = self.client.get(
            "/tests/images/secretly-a-gif.jpg.resize.1066x600.png"
        )
        body = response.data.decode("utf-8")
        assert response.status_code == 400
        assert "tests/images/secretly-a-gif.jpg is not a supported file type" in body

    def test_too_large_a_crop(self):
        response = self.client.get("/tests/images/test.png.crop.640x276360.png")
        assert response.status_code == 400
        body = response.data.decode("utf-8")
        assert "640x276360 is too big" in body

    def test_too_large_a_resize(self):
        response = self.client.get("/tests/images/test.png.resize.640x276360.png")
        assert response.status_code == 400
        body = response.data.decode("utf-8")
        assert "640x276360 is too big" in body

    def test_crop_with_single_parameter(self):
        response = self.client.get("/tests/images/test.png?crop=8000")
        assert response.status_code == 400
        body = response.data.decode("utf-8")
        assert "crop requires width and height" in body
