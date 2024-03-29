from image_builder.api.controllers import security_controller
from image_builder.api.settings import Settings


class TestSecurity:
    def test_validate_scope(self):
        assert security_controller.validate_scope(None, None) is True
        assert security_controller.validate_scope([], []) is True
        assert security_controller.validate_scope(["test"], None) is True

    def test_check_api_key(self):
        Settings.apiKey = None
        assert security_controller.check_api_key('foo') is None

        Settings.apiKey = 'bar'
        assert security_controller.check_api_key('bar') == {'scope': ['apiKey']}

    def test_token_info(self, mocker):
        mock = mocker.MagicMock()
        mock.ok = False
        Settings.oidc_introspection_endpoint_uri = ""
        result = security_controller.token_info("ACCESS_TOKEN")
        assert result is None
        Settings.oidc_introspection_endpoint_uri = "test"
        mocker.patch("image_builder.api.controllers.security_controller.session.post", return_value=mock)
        result = security_controller.token_info("ACCESS_TOKEN")
        assert result is None
        mock.ok = True
        mock.json.return_value = {'active': False}
        result = security_controller.token_info("ACCESS_TOKEN")
        assert result is None
        mock.json.return_value = {'scope': ['email']}
        result = security_controller.token_info("ACCESS_TOKEN")
        assert result["scope"][0] == 'email'
