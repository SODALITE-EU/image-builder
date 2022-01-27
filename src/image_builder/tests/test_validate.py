from image_builder.api.service.image_builder_service import validate
from image_builder.api.openapi.models import BuildParams


class TestValidate:
    def test_dockerfile_1(self):
        build_params = {
            "source": {
                "dockerfile": {
                    "url": "http://url/to/file",
                    "username": "user",
                    "password": "pass"
                },
                "build_context": {
                    "url": "https://github.com/mihaTrajbaric/image-builder-test-files",
                    "username": "user",
                    "password": "pass",
                    "subdir": "no_context"
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
        valid, message = validate(BuildParams.from_dict(build_params))
        assert valid
        assert message == ''

    def test_dockerfile_2(self):
        build_params = {
            "source": {
                "dockerfile": {
                    "url": "http://url/to/file",
                    "username": "miha",
                    "password": "pass"
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
        valid, message = validate(BuildParams.from_dict(build_params))
        assert valid
        assert message == ''

    def test_git(self):
        build_params = {
            "source": {
                "git_repo": {
                    "url": "https://gitlab.com/wds-co/SnowWatch-SODALITE.git",
                    "username": "repo_username",
                    "password": "repo_password",
                    "dockerfile": "MountainRelevanceClassifier/Dockerfile",
                    "workdir": "."
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
        valid, message = validate(BuildParams.from_dict(build_params))
        assert valid
        assert message == ''

    def test_fail(self):
        build_params = {
            "source": {
                "git_repo": {
                    "url": "string",
                    "version": "HEAD",
                    "username": "string",
                    "password": "string",
                    "workdir": ".",
                    "dockerfile": "Dockerfile"
                },
                "dockerfile": {
                    "url": "string",
                    "username": "string",
                    "password": "string"
                },
                "build_context": {
                    "url": "string",
                    "username": "string",
                    "password": "string",
                    "subdir": "string"
                }
            },
            "target": {
                "images": [
                    {
                        "image": "image-builder",
                        "tag": "latest",
                        "base": "python:3.8.8"
                    }
                ],
                "platforms": [
                    "linux/amd64"
                ]
            }
        }
        valid, message = validate(BuildParams.from_dict(build_params))
        assert not valid
        assert message != ''
