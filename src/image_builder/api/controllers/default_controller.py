import json

import connexion

from image_builder.api.log import get_logger
from image_builder.api.openapi.models.build_params import BuildParams
from image_builder.api.openapi.models.invocation import Invocation
from image_builder.api.service.invocation_service import InvocationService

logger = get_logger(__name__)
invocation_service = InvocationService()


def get_status(build_id):
    """check status

    :param build_id: Id of image-building Invocation
    :type build_id: str

    :rtype: Invocation
    """
    inv = invocation_service.load_invocation(build_id)
    return inv, 200


def post_build():
    """Request building image

     # noqa: E501

    :rtype: Invocation
    """
    build_params = BuildParams.from_dict(connexion.request.get_json())

    logger.info(json.dumps(build_params.to_dict(), indent=2))

    return invocation_service.invoke(build_params), 202
