import pytest
import yaml
from app.main.service.image_builder_service import validate
import os
from pathlib import Path
import shutil
import docker
from docker import DockerClient
import json
import functools

tosca_path = (Path(__file__).parent.parent / "main" / "service" / "image_builder" / "TOSCA")
tests_path = tosca_path / 'playbooks' / 'tests'


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


def json_to_yaml(json_path: Path, yaml_path: Path, registry_ip: str):
    """
    transforms json test to yaml test
    """
    json_test = json.load(json_path.open('r'))

    yaml_test = validate(json_test)
    yaml_test['target']['registry_ip'] = registry_ip

    yaml_path.open('w').write(yaml.dump(yaml_test))


def run_test(test_name: str):
    """
    Runs yaml test and returns exit_code
    """
    test_path = tests_path / 'tests-yaml' / f'{test_name}.yaml'
    script = f"cd {tosca_path}\n" \
             f"opera deploy --inputs {test_path} docker_image_definition.yaml\n"
    exit_code = os.system(script)
    shutil.rmtree((tosca_path / ".opera"), ignore_errors=True)
    return exit_code


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

    for json_test_path in (tests_path / 'tests-json').glob("*"):
        yaml_test_path = tests_path / 'tests-yaml' / (str(json_test_path.stem) + '.yaml')
        json_to_yaml(json_test_path, yaml_test_path, registry_ip)

    # run test
    check_docker_image = functools.partial(check_image, client, registry_ip)
    yield run_test, check_docker_image

    # cleanup
    delete_images(client, 'tests')
