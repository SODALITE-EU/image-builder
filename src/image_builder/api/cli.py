import os

import connexion

from image_builder.api.log import get_logger
from image_builder.api.openapi import encoder
from image_builder.api.service.sqldb_service import PostgreSQL, SqlDBFailedException
from image_builder.api.settings import Settings
from time import sleep

DEBUG = os.getenv("DEBUG", "false") == "true"
logger = get_logger(__name__)
Settings.load_settings()


def main():
    attempts = 0
    while attempts < 10:
        try:
            PostgreSQL.initialize()
            logger.info("Successfully connected to database")
            break
        except SqlDBFailedException as e:
            attempts += 1
            sleep(1)
            logger.warning(e)

    if DEBUG:
        logger.info("Running in debug mode: flask backend.")
        server = "flask"
    else:
        logger.info("Running in production mode: tornado backend.")
        server = "tornado"

    app = connexion.App(__name__, specification_dir="./openapi/openapi/", server=server, options=dict(
        serve_spec=True,
        swagger_ui=True
    ))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api("openapi.yaml", arguments={"title": "SODALITE Image Builder REST API"}, pythonic_params=True)
    app.run(port=8080, debug=DEBUG)


def test():
    app = connexion.App(__name__, specification_dir="./openapi/openapi/", options=dict(
        serve_spec=False,
        swagger_ui=False
    ))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api("openapi.yaml")
    app.testing = True
    return app


if __name__ == "__main__":
    main()
