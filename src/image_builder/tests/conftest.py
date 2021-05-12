import datetime
import functools
import json
import os
import shutil
import uuid
from pathlib import Path
from contextlib import contextmanager


import docker
import psutil
import pytest
from docker import DockerClient

from image_builder.api.cli import test
from image_builder.api.openapi.models import BuildParams, Invocation, InvocationState
from image_builder.api.service.image_builder_service import validate
from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.storage import Storage
from opera.error import OperationError


tosca_path = (Path(__file__).parent.parent / "TOSCA")
tests_path = Path(__file__).parent / 'integration'


def pytest_addoption(parser):
    parser.addoption("--registry_ip", action="store", help='api url', default='localhost')


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

    yaml_test = validate(BuildParams.from_dict(json_test))
    yaml_test['target']['registry_ip'] = registry_ip
    yaml_test['custom_workdir'] = 'workdir'

    return yaml_test

    # yaml_path.open('w').write(yaml.dump(yaml_test))


def run_test(registry_ip: str, test_name: str):
    """
    Runs yaml test and returns exit_code
    """
    test_path = tests_path / 'build_params' / f'{test_name}.json'

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

    image_name_path = tests_path / 'image_names' / (test_name + '.txt')

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


@pytest.fixture()
def generic_build_params():
    return BuildParams.from_dict({
        "source_type": "dockerfile",
        "source_url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile",
        "target_image_name": "tests/no_context",
        "target_image_tag": "latest"
    })


@pytest.fixture()
def generic_invocation():
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    inv = Invocation()
    inv.invocation_id = uuid.uuid4()
    inv.build_params = BuildParams.from_dict({
        "source_type": "dockerfile",
        "source_url": "https://raw.githubusercontent.com/mihaTrajbaric/image-builder-test-files/master/no_context/Dockerfile",
        "target_image_name": "tests/no_context",
        "target_image_tag": "latest"
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


@contextmanager
def cwd(path):
    old_pwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_pwd)
