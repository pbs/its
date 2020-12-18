from unittest import TestCase
from unittest.mock import Mock, patch

from werkzeug.exceptions import Unauthorized


class TestLoginRequired(TestCase):
    @classmethod
    @patch('its.settings.NAMESPACES', {"test": {
        "loader": "s3", "bucket": "", "key": "test", "secret": "test"}})
    def setUpClass(self):
        from its.application import APP
        from its.auth import login_required

        APP.config["TESTING"] = True
        self.APP = APP
        self.decorated_func = login_required(Mock(return_value=True))

    def test_invalid_namespace(self):
        with self.APP.test_request_context(), self.assertRaises(
                Unauthorized) as unauth_exc:
            self.decorated_func(namespace='invalid')
            assert 401 == unauth_exc.exception.code
        assert unauth_exc.exception.description == 'Invalid namespace.'

    def test_missing_credentials(self):
        with self.APP.test_request_context(), self.assertRaises(
                Unauthorized) as unauth_exc:
            self.decorated_func(namespace='test')
        assert unauth_exc.exception.description == \
               'Authentication credentials were not provided.'

    def test_invalid_credentials(self):
        with self.APP.test_request_context(environ_base={
            "HTTP_AUTHORIZATION": "invalid"}), self.assertRaises(
                Unauthorized) as unauth_exc:
            self.decorated_func(namespace='test')
        assert unauth_exc.exception.description == \
               'Invalid authentication credentials.'

    def test_valid_credentials(self):
        with self.APP.test_request_context(environ_base={
                "HTTP_AUTHORIZATION": "dGVzdDp0ZXN0"}):
            response = self.decorated_func(namespace='test')
        assert response

