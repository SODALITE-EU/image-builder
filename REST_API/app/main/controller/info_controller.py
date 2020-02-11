from flask_restplus import Resource

from app.main.util.decorator import token_required
from app.main.util.dto import InfoDto
from ..service.info_service import check_status, check_log

api = InfoDto.api
info_params = InfoDto.check_info


@api.route('/status/<session_token>')
@api.param('session_token', 'Token of image-building session')
class Status(Resource):
    @token_required
    @api.response(201, 'Success')
    @api.response(202, 'Building')
    @api.response(500, 'Job failed')
    @api.doc('check status of image building job')  # , security=None)
    def get(self, session_token):
        """check status"""

        return check_status(session_token)


@api.route('/log/<session_token>')
@api.param('session_token', 'Token of image-building session')
class Log(Resource):
    @token_required
    @api.response(200, 'Success')
    @api.response(404, 'Logfile not found')
    @api.doc('check log of image building job')  # , security=None)
    def get(self, session_token):
        """check log"""

        return check_log(session_token)
