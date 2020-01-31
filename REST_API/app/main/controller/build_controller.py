from flask import request
from flask_restplus import Resource

from app.main.util.decorator import token_required
from ..service.image_builder_service import build_image
from ..util.dto import BuildDto

api = BuildDto.api
build_params = BuildDto.build_params


@api.route('/')
class BuildImage(Resource):
    @token_required
    @api.expect(build_params, validate=True)
    @api.response(202, 'Build job accepted')
    @api.doc('Post build job')  # , security=None)
    def post(self):
        """Request building image"""
        data = request.json

        return build_image(data)
