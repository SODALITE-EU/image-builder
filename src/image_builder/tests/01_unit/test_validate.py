from image_builder.api.service.image_builder_service import validate
from image_builder.api.openapi.models import BuildParams


class TestValidate:
    def test_dockerfile_1(self):
        build_params = {
            "source_type": "dockerfile",
            "source_url": "https://link/to/Dockerfile",
            "source_username": "my_optional_username",
            "source_password": "my_optional_password",
            "build_context": {
                "url": "https://url/to/git/repo/with/build_context.git",
                "username": "my_username",
                "password": "my_password_or_token"
            },
            "target_image_name": "my_image_name",
            "target_image_tag": "my_image_tag"
        }
        valid, message = validate(BuildParams.from_dict(build_params))
        assert valid
        assert message == ''

    def test_dockerfile_2(self):
        build_params = {
            "source_type": "dockerfile",
            "source_url": "https://link/to/Dockerfile",
            "target_image_name": "my_image_name",
            "target_image_tag": "my_image_tag"
        }
        valid, message = validate(BuildParams.from_dict(build_params))
        assert valid
        assert message == ''

    def test_git(self):
        build_params = {
            "source_type": "git",
            "source_repo": {
                "url": "https://url/to/repo.git",
                "username": "repo_username",
                "password": "repo_password",
                "dockerfile": "path/to/Dockerfile",
                "workdir": "."
            },
            "target_image_name": "my_image_name",
            "target_image_tag": "my_image_tag"
        }
        valid, message = validate(BuildParams.from_dict(build_params))
        assert valid
        assert message == ''

    def test_fail(self):
        build_params = {
            "source_type": "git",
            "build_context": {
                "url": "build_context_url",
                "username": "build_context_username",
                "password": "build_context_password",
                "subdir": "build_context_workdir"
            },
            "source_password": "source_password",
            "source_repo": {
                "url": "repo_url",
                "username": "repo_username",
                "password": "repo_password",
                "workdir": "docker_workdir",
                "dockerfile": "git_dockerfile"
            },
            "source_url": "source_url",
            "source_username": "source_username",
            "target_image_name": "target_image_name",
            "target_image_tag": "latest",
            "target_images": [
                {
                    "base": "base",
                    "image": "image",
                    "tag": "tag"
                },
                {
                    "base": "base",
                    "image": "image",
                    "tag": "tag"
                }
            ]
        }
        valid, message = validate(BuildParams.from_dict(build_params))
        assert not valid
        assert message != ''
