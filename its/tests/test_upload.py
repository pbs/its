import io
from unittest import TestCase
from unittest.mock import patch


class TestUpload(TestCase):
    @classmethod
    @patch('its.settings.NAMESPACES', {"test": {
        "loader": "s3", "bucket": "", "key": "test", "secret": "test"}})
    def setUpClass(self):
        from its.application import APP

        APP.config["TESTING"] = True
        self.client = APP.test_client()

    def test_missing_image(self):
        response = self.client.post(
            "/test/upload",
            content_type='multipart/form-data',
            headers={"Authorization": "dGVzdDp0ZXN0"}
        )
        assert response.status_code == 400
        assert "Please provide an image to upload." in response.data.decode(
            "utf-8")

    def test_invalid_image_format(self):
        response = self.client.post(
            "/test/upload",
            data={'file': (io.BytesIO(b"test"), 'test.invalid')},
            content_type='multipart/form-data',
            headers={"Authorization": "dGVzdDp0ZXN0"}
        )
        assert response.status_code == 400
        assert "Invalid image format." in response.data.decode("utf-8")

    def test_successful_upload(self):
        response = self.client.post(
            "/test/upload",
            data={'file': (io.BytesIO(b"test"), 'test.jpg')},
            content_type='multipart/form-data',
            headers={"Authorization": "dGVzdDp0ZXN0"}
        )
        assert response.status_code == 204
