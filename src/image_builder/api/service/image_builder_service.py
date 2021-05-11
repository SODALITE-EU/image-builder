import tempfile
from distutils import dir_util
import json

from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.outputs import outputs as opera_outputs
from opera.storage import Storage

from image_builder.api.log import get_logger
from image_builder.api.openapi.models import Invocation, BuildParams
from image_builder.api.settings import Settings
from image_builder.api.util import image_builder_util

logger = get_logger(__name__)


def validate(data: BuildParams):

    try:
        build_context = data.build_context.to_dict()
    except AttributeError:
        build_context = None

    try:
        repo = data.source_repo.to_dict()
    except AttributeError:
        repo = None

    try:
        image_variants = [{'image': element.image, 'tag': element.tag, 'base': element.base or None}
                          for element in data.target_images]
    except TypeError:
        image_variants = None

    return {
        "source": {
            "type": data.source_type,
            "url": data.source_url,
            "username": data.source_username,
            "password": data.source_password,
            "build_context": build_context,
            "repo": repo
        },
        "target": {
            "registry_ip": Settings.registry_ip,
            "image_name": data.target_image_name,
            "image_tag": data.target_image_tag,
            "images": image_variants,
        }
    }


def build_image(inv: Invocation):

    with tempfile.TemporaryDirectory() as workdir:
        dir_util.copy_tree(Settings.TOSCA_path, workdir)
        with image_builder_util.cwd(workdir):
            opera_storage = Storage.create(".opera")
            service_template = "docker_image_definition.yaml"
            build_params = validate(inv.build_params)
            logger.info(json.dumps(build_params))
            opera_deploy(service_template, build_params, opera_storage,
                         verbose_mode=False, num_workers=1, delete_existing_state=True)
            return opera_outputs(opera_storage)
