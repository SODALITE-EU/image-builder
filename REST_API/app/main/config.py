import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 24*60))
    REGISTRY_IP = os.getenv('REGISTRY_IP', 'localhost')
    DEBUG = False


class DevelopmentConfig(Config):
    print("running development configuration")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'image_builder_main.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'image_builder_test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    print("running production configuration")
    DEBUG = False
    try:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    except KeyError:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'image_builder_main.db')
        print(f'using developement database: {SQLALCHEMY_DATABASE_URI}')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
session_timeout = Config.SESSION_TIMEOUT
registry_ip = Config.REGISTRY_IP
print(f'Config:\n'
      f'SESSION_TIMEOUT: {session_timeout} minutes\n'
      f'REGISTRY_IP: {registry_ip}\n'
      f'SECRET_KEY: {"default" if key == "my_precious_secret_key" else "****"}')
