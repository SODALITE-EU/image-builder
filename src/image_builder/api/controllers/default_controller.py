import connexion
import json

from image_builder.api.openapi.models.build_params import BuildParams  # noqa: E501
from image_builder.api.openapi.models.invocation import Invocation  # noqa: E501
from image_builder.api.openapi import util
from image_builder.api.service import image_builder_service
from image_builder.api.service.invocation_service import InvocationService

from image_builder.api.log import get_logger

logger = get_logger(__name__)
invocation_service = InvocationService()


def get_status(build_id):  # noqa: E501
    """check status

     # noqa: E501

    :param build_id: Id of image-building Invocation
    :type build_id: str

    :rtype: Invocation
    """
    inv = invocation_service.load_invocation(build_id)
    return inv, 200


def post_build():  # noqa: E501
    """Request building image

     # noqa: E501

    :rtype: Invocation
    """
    # if connexion.request.is_json:
    build_params = BuildParams.from_dict(connexion.request.get_json())  # noqa: E501

    logger.info(json.dumps(build_params.to_dict(), indent=2))

    return invocation_service.invoke(build_params), 202
