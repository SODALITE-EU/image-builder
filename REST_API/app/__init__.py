# app/__init__.py

from flask import Blueprint
from flask_restplus import Api

from .main.controller.auth_controller import api as auth_ns
from .main.controller.build_controller import api as build_ns
from .main.controller.info_controller import api as info_ns
from .main.controller.user_controller import api as user_ns
from .main.util.dto import authorizations as auth

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='SODALITE image builder REST API',
          version='beta',
          description='RESTful tool for building docker images',
          security='Bearer token',
          authorizations=auth
          )

api.add_namespace(user_ns, path='/user')
api.add_namespace(auth_ns)
api.add_namespace(build_ns, path='/build')
api.add_namespace(info_ns, path='/info')
