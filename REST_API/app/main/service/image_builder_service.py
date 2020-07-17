import os
import shutil
import subprocess
import uuid
from distutils import dir_util

from pathlib import Path
import yaml

from app.main.service import ImageBuilderConfig
from ..config import registry_ip


def validate(data: dict):
    source_type = 'dockerfile' if data['source_type'].casefold() == 'dockerfile' else 'tar' \
        if data['source_type'].casefold() == 'tar' else None
    if not source_type:
        print('invalid source_type')
        return None
    url = data['source_url']
    url_username = data.get('source_username', None)
    url_pass = data.get('source_password', None)
    target_registry_ip = registry_ip
    image_name = data.get('target_image_name', None)
    image_tag = data.get('target_image_tag', None)
    build_context = data.get('build_context', None)

    try:
        image_variants = [{'image': element.get('image'), 'tag': element.get('tag'), 'base': element.get('base', None)}
                          for element in data['target_images']]
    except KeyError:
        image_variants = None

    return {
        "source": {
            "type": source_type,
            "url": url,
            "username": url_username,
            "password": url_pass,
            "build_context": build_context
        },
        "target": {
            "registry_ip": target_registry_ip,
            "image_name": image_name,
            "image_tag": image_tag,
            "images": image_variants,
        }
    }


def read_input(path):
    return yaml.safe_load(open(path, 'r'))


def build_image(data: dict):

    basedir = os.path.abspath(os.path.dirname(__file__))

    session_token = str(uuid.uuid4())

    logfile = ImageBuilderConfig.logfile_name
    timestamp_start = ImageBuilderConfig.datetime_now_to_string()
    run_path = f'{basedir}/image_builder/run/{session_token}'
    TOSCA_path = f'{basedir}/image_builder/TOSCA'
    deploy_path = f'{basedir}/image_builder/scripts'
    _input = validate(data)

    shutil.rmtree(run_path, ignore_errors=True)
    os.makedirs(run_path)
    dir_util.copy_tree(TOSCA_path, run_path)

    with open(f'{run_path}/inputs.yaml', 'w') as inputs:
        inputs.write(yaml.dump(_input))

    command = ['./deploy.sh', run_path, session_token, logfile, timestamp_start]
    subprocess.Popen(command, cwd=deploy_path)

    response_object = {
        'status': 'Accepted',
        'message': 'Successfully submitted docker image building job.',
        'session_token': session_token
    }
    return response_object, 202


if __name__ == '__main__':
    build_image(dict())
