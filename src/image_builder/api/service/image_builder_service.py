import tempfile
from distutils import dir_util
import json

from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.outputs import outputs as opera_outputs
from opera.storage import Storage

from image_builder.api.log import get_logger
from image_builder.api.openapi.models import Invocation, BuildParams, SourceType
from image_builder.api.settings import Settings
from image_builder.api.util import image_builder_util

logger = get_logger(__name__)


def validate(data: BuildParams):
    """
    Makes sure a valid combination of params have been provided.
    """
    message = ''
    params = {
        "source_type": bool(data.source_type),
        "build_context": bool(data.build_context),
        "source_password": bool(data.source_password),
        "source_repo": bool(data.source_repo),
        "source_url": bool(data.source_url),
        "source_username": bool(data.source_username),
        "target_image_name": bool(data.target_image_name),
        "target_image_tag": bool(data.target_image_name),
        "target_images": bool(data.target_images)
    }
    dest_params_all = {'target_image_name', 'target_image_tag', 'target_images'}
    dest_params = {key for key, value in params.items() if value and key in dest_params_all}
    dest_option_1 = {'target_images'}
    dest_option_2 = {'target_image_name', 'target_image_tag'}
    source_params = {key for key, value in params.items() if value} - dest_params

    if data.source_type == SourceType.GIT:
        minimal = {'source_type', 'source_repo'}
        maximal = {'source_type', 'source_repo'}

    elif data.source_type == SourceType.TAR:
        minimal = {'source_type', 'source_url'}
        maximal = {'source_type', 'source_url', 'source_username', 'source_password'}

    elif data.source_type == SourceType.DOCKERFILE:
        minimal = {'source_type', 'source_url'}
        maximal = {'source_type', 'source_url', 'source_username', 'source_password', 'build_context'}
    else:
        return False

    source_valid = minimal <= source_params <= maximal
    if not source_valid:
        message += f"Required source properties: {list(minimal)}, " \
                   f"allowed source properties: {list(maximal)}, " \
                   f"got {list(source_params)}\n"

    dest_valid = dest_params == dest_option_1 or dest_params == dest_option_2
    if not dest_valid:
        message += f"Destination must be described with either {list(dest_option_1)} or {list(dest_option_2)}, " \
                   f"got {list(dest_params)}"

    valid = source_valid and dest_valid
    if not valid:
        message = f"Missing / redundant properties for source_type=='{data.source_type}'.\n" + message

    return source_valid and dest_valid, message


def transform_build_params(data: BuildParams):
    try:
        build_context = {k: v for k, v in data.build_context.to_dict().items() if v is not None}
    except AttributeError:
        build_context = None

    try:
        repo = {k: v for k, v in data.source_repo.to_dict().items() if v is not None}
    except AttributeError:
        repo = None

    try:
        image_variants = [{'image': element.image, 'tag': element.tag, 'base': element.base or None}
                          for element in data.target_images]
        # TODO remove none from image_variants
    except TypeError:
        image_variants = None

    source = {
            "type": data.source_type,
            "url": data.source_url,
            "username": data.source_username,
            "password": data.source_password,
            "build_context": build_context,
            "repo": repo
        }
    target = {
            "registry_ip": Settings.registry_ip,
            "image_name": data.target_image_name,
            "image_tag": data.target_image_tag,
            "images": image_variants,
        }
    return {
        "source": {k: v for k, v in source.items() if v is not None},
        "target": {k: v for k, v in target.items() if v is not None}
    }


def build_image(inv: Invocation):
    with tempfile.TemporaryDirectory() as workdir:
        dir_util.copy_tree(Settings.TOSCA_path, workdir)
        with image_builder_util.cwd(workdir):
            opera_storage = Storage.create(".opera")
            service_template = "docker_image_definition.yaml"
            build_params = transform_build_params(inv.build_params)
            logger.info(json.dumps(build_params))
            opera_deploy(service_template, build_params, opera_storage,
                         verbose_mode=False, num_workers=1, delete_existing_state=True)
            return opera_outputs(opera_storage)


if __name__ == '__main__':
    from pathlib import Path
    import yaml
    import os

    Settings.registry_ip = 'localhost:5000'
    json_path = Path(
        '/home/mihaeltrajbaric/projects/SODALITE/SODALITE-EU-github/image-builder/build-params/JSON_(API)')
    yaml_path = Path('/home/mihaeltrajbaric/projects/SODALITE/SODALITE-EU-github/image-builder/build-params/YAML_(TOSCA)')
    json_files = [path for path in json_path.rglob('*') if path.is_file()]
    for file_path in json_files:
        print(file_path.relative_to(json_path))
        build_params = json.load(file_path.open('r'))
        transformed = transform_build_params(BuildParams.from_dict(build_params))
        new_path = Path(str(file_path).replace(str(json_path), str(yaml_path)).replace('.json', '.yaml'))
        if not new_path.parent.exists():
            os.makedirs(new_path.parent, exist_ok=True)
        yaml.dump(transformed, new_path.open('w'))

