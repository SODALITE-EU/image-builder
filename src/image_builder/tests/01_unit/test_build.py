from image_builder.api.service.image_builder_service import build_image


class TestBuildImage:
    
    def test_success(self, mocker, generic_invocation):
        mock_opera_outputs = mocker.MagicMock(name='opera', return_value={})
        mocker.patch('image_builder.api.service.image_builder_service.opera_outputs', new=mock_opera_outputs)
        mocker.patch('image_builder.api.service.image_builder_service.opera_deploy', return_value=None)

        outputs = build_image(generic_invocation)
        # outputs are not yet implemented in docker_image_definition.yaml
        assert outputs == {}


