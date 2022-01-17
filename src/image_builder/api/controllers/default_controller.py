import json

import connexion

from image_builder.api.log import get_logger
from image_builder.api.openapi.models import BuildParams, Invocation, BuildingStarted
from image_builder.api.service.invocation_service import InvocationService
from image_builder.api.service.image_builder_service import validate, mask_password_inv

logger = get_logger(__name__)
invocation_service = InvocationService()


def get_status(invocation_id):
    """check status

    :param invocation_id: Id of image-building Invocation
    :type invocation_id: str

    :rtype: Invocation
    """
    logger.debug(f"Checking status for invocation with ID {invocation_id}")
    inv = invocation_service.load_invocation(invocation_id)
    if not inv:
        return f"Invocation with ID {invocation_id} not found", 404
    try:
        return mask_password_inv(inv), 200
    except Exception as e:
        logger.error(e)
        return inv, 200


def post_build():
    """Request building image

    :rtype: Invocation
    """
    build_params = BuildParams.from_dict(connexion.request.get_json())
    valid, message = validate(build_params)
    if not valid:
        return message, 400

    logger.debug(json.dumps(build_params.to_dict(), indent=2))

    inv = invocation_service.invoke(build_params)

    return BuildingStarted(inv.invocation_id), 202
