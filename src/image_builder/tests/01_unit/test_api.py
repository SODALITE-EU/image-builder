import json
import uuid

from assertpy import assert_that


class TestBuild:
    build_data = {
        "source": {
            "git_repo": {
                "url": "https://gitlab.com/wds-co/SnowWatch-SODALITE.git"
            }
        },
        "target": {
            "images": [
                {
                    "image": "xopera-rest-api",
                    "tag": "latest"
                }
            ]
        }
    }

    def test_success(self, mocker, generic_invocation, generic_build_params, client):
        mock_invoke = mocker.MagicMock(name='invoke', return_value=generic_invocation)
        mocker.patch('image_builder.api.service.invocation_service.InvocationService.invoke', new=mock_invoke)

        resp = client.post("/build/", data=json.dumps(self.build_data), content_type='application/json')
        assert resp.status_code == 202
        mock_invoke.assert_called_with(generic_build_params)


class TestStatus:

    def test_success(self, mocker, generic_invocation, client):
        mock_invoke = mocker.MagicMock(name='invoke', return_value=generic_invocation)
        mocker.patch('image_builder.api.service.invocation_service.InvocationService.load_invocation', new=mock_invoke)

        job_id = uuid.uuid4()
        resp = client.get(f"/status/{job_id}")
        assert resp.status_code == 200
        mock_invoke.assert_called_with(str(job_id))
        assert_that(resp.json).contains_only(*[k for k in generic_invocation.to_dict().keys() if
                                               generic_invocation.to_dict()[k] is not None])
