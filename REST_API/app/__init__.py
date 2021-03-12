# app/__init__.py

from flask import Blueprint
from flask_restplus import Api

from .main.controller.build_controller import api as build_ns
from .main.controller.info_controller import api as info_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='SODALITE image builder REST API',
          version='0.3.2',
          description='RESTful tool for building docker images'
          )

api.add_namespace(build_ns, path='/build')
api.add_namespace(info_ns, path='/info')
