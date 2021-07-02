import datetime
import functools
import json
import os
import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path

import docker
import psutil
import pytest
from docker import DockerClient
from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.error import OperationError
from opera.storage import Storage

from image_builder.api.cli import test
from image_builder.api.openapi.models import BuildParams, Invocation, InvocationState
from image_builder.api.service.image_builder_service import transform_build_params

tosca_path = (Path(__file__).parent.parent / "TOSCA")
test_build_params = Path(__file__).parent / '02_integration' / 'build_params'


def pytest_addoption(parser):
    parser.addoption("--registry_ip", action="store", help='registry url', default='localhost')


def find_images(client: DockerClient, substring: str):
    """
    returns list of docker images with substring in image_tag

    """
    image_list = client.images.list()

    image_list_filtered = [image for image in image_list if
                           any(substring in string for string in image.attrs['RepoTags'])]
    return image_list_filtered


def delete_images(client: DockerClient, substring: str):
    """
    deletes images with substring in image_tag

    """
    image_list = find_images(client, substring)

    for image in image_list:
        client.images.remove(image=image.id, force=True)


def json_to_yaml(test_path: Path, registry_ip: str):
    """
    transforms json test to yaml test
    """
    json_test = json.load(test_path.open('r'))

    yaml_test = transform_build_params(BuildParams.from_dict(json_test))
    yaml_test['target']['registry_ip'] = registry_ip
    yaml_test['custom_workdir'] = 'workdir'

    return yaml_test


def run_test(registry_ip: str, test_name: str):
    """
    Runs yaml test and returns exit_code
    """
    test_path = test_build_params / f'{test_name}.json'

    inputs = json_to_yaml(test_path, registry_ip)
    with cwd(tosca_path):
        opera_storage = Storage.create('.opera')
        try:
            opera_deploy('docker_image_definition.yaml', inputs, opera_storage,
                         verbose_mode=False, num_workers=1, delete_existing_state=True)
        except OperationError:
            return 1
        finally:
            shutil.rmtree((tosca_path / ".opera"), ignore_errors=True)
    return 0


def check_image(client: DockerClient, registry_ip: str, test_name: str):
    """
    Check if docker image(s) have been created
    """

    image_name_path = test_build_params / (test_name + '.name')

    # read file with image_names
    for line in image_name_path.open('r').readlines():
        image_name = line.replace('registry_ip', registry_ip).rstrip()

        # check if docker image exists
        client.images.get(image_name)


@pytest.fixture(scope="package")
def core_test_tools(pytestconfig):
    client = docker.from_env()

    # remove previous test images
    delete_images(client, 'tests')

    # move tests to yaml
    registry_ip = pytestconfig.getoption("registry_ip")

    # run test
    check_docker_image = functools.partial(check_image, client, registry_ip)
    run_integration_test = functools.partial(run_test, registry_ip)
    yield run_integration_test, check_docker_image

    # cleanup
    delete_images(client, 'tests')


@contextmanager
def cwd(path):
    old_pwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_pwd)


@pytest.fixture()
def generic_build_params():
    return BuildParams.from_dict({
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
    })


@pytest.fixture()
def generic_invocation():
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    inv = Invocation()
    inv.invocation_id = uuid.uuid4()
    inv.build_params = BuildParams.from_dict({
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
    })
    inv.state = InvocationState.PENDING
    inv.timestamp_submission = now.isoformat()
    inv.response = None
    return inv


@pytest.fixture(scope="session")
def client(session_mocker):
    """An application for the tests."""
    os.environ['LOG_LEVEL'] = 'debug'
    session_mocker.patch('connexion.decorators.security.get_authorization_info', return_value={'scope': ['apiKey']})
    with test().app.test_client() as client:
        yield client
    kill_tree(os.getpid(), including_parent=False)


def kill_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        try:
            child.kill()
        except psutil.NoSuchProcess:
            pass

    if including_parent:
        parent.kill()
