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
import copy

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


def mask_password_inv(inv: Invocation):
    """
    replaces all password values with '****'
    """
    if inv.build_params.target.registry.password:
        inv.build_params.target.registry.password = '****'

    if inv.build_params.source.git_repo:
        if inv.build_params.source.git_repo.password:
            inv.build_params.source.git_repo.password = '****'

    if inv.build_params.source.dockerfile:
        if inv.build_params.source.dockerfile.password:
            inv.build_params.source.dockerfile.password = '****'

    return inv


def mask_password(obj: dict):
    """
    replaces all password values with '****'
    """

    def replace_in_dict(obj_dict, key, replace_value):
        for k, v in obj_dict.items():
            if isinstance(v, dict):
                obj_dict[k] = replace_in_dict(v, key, replace_value)
            elif isinstance(v, list):
                obj_dict[k] = replace_in_list(v, key, replace_value)
        if key in obj_dict:
            obj_dict[key] = replace_value
        return obj_dict

    def replace_in_list(obj_list, key, replace_value):
        for i, item in enumerate(obj_list):
            if isinstance(item, dict):
                obj_list[i] = replace_in_dict(item, key, replace_value)
            elif isinstance(item, list):
                obj_list[i] = replace_in_list(item, key, replace_value)
        return obj_list

    return replace_in_dict(copy.deepcopy(obj), 'password', '****')


def transform_build_params(data: BuildParams):
    build_params = data.to_dict()

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
            logger.info(json.dumps(mask_password(build_params)))
            opera_deploy(service_template, build_params, opera_storage,
                         verbose_mode=False, num_workers=1, delete_existing_state=True)
            return opera_outputs(opera_storage)
