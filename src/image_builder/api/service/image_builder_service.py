import tempfile
from distutils import dir_util
import json
from pathlib import PurePath

from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.outputs import outputs as opera_outputs
from opera.storage import Storage

from image_builder.api.log import get_logger
from image_builder.api.openapi.models import Invocation, BuildParams
from image_builder.api.settings import Settings
from image_builder.api.util import image_builder_util

logger = get_logger(__name__)


def validate(data: BuildParams):
    """
    Makes sure a valid combination of params have been provided.
    """
    git_repo = bool(data.source.git_repo)
    dockerfile = bool(data.source.dockerfile)
    build_context = bool(data.source.build_context)
    git_valid = git_repo and not dockerfile and not build_context
    dockerfile_valid = dockerfile and not git_repo

    if not (git_valid or dockerfile_valid):
        return False, "Only one of build sources (git_repo, dockerfile) can be used.\n" \
                      "git_context can only be used in combination with dockerfile"

    return True, ""


def transform_build_params(data: BuildParams):
    build_params = data.to_dict()
    # if not build_params['target']['registry']:
    #     logger.debug(f'Changing registry_ip to {Settings.registry_ip}')
    #     build_params['target']['registry'] = dict(url=Settings.registry_ip)
    # else:
    #     logger.debug(f"Registry_ip={build_params['target']['registry']['url']}")

    def remove_none_dict(_dict: dict):
        dict_keys = list(_dict.keys())
        for key in dict_keys:
            value = _dict[key]
            if isinstance(value, dict):
                remove_none_dict(value)
            elif isinstance(value, list):
                remove_none_list(value)
            elif _dict[key] is None:
                del _dict[key]

    def remove_none_list(_list: list):
        _list = [item for item in _list if item is not None]
        for item in _list:
            if isinstance(item, dict):
                remove_none_dict(item)

    remove_none_dict(build_params)
    return build_params


def build_image(inv: Invocation):
    with tempfile.TemporaryDirectory() as workdir:
        dir_util.copy_tree(Settings.TOSCA_path, workdir)
        with image_builder_util.cwd(workdir):
            opera_storage = Storage.create(".opera")
            service_template = PurePath(workdir) / "docker_image_definition.yaml"
            build_params = transform_build_params(inv.build_params)
            logger.info(json.dumps(build_params))
            opera_deploy(service_template, build_params, opera_storage,
                         verbose_mode=False, num_workers=1, delete_existing_state=True)
            return opera_outputs(opera_storage)
