import json
import os
from pathlib import Path
import copy

from image_builder.api.log import get_logger

logger = get_logger(__name__)


class Settings:
    implementation_dir = Path(__file__).absolute().parent.parent
    TOSCA_path = implementation_dir.parent / "TOSCA"

    # PostgreSQL config
    sql_config = None
    invocation_table = 'invocation'

    # Authorization and Authentication config
    oidc_introspection_endpoint_uri = None
    oidc_client_id = None
    oidc_client_secret = None
    apiKey = None
    connection_protocols = ["http://", "https://"]

    @staticmethod
    def load_settings():
        Settings.oidc_introspection_endpoint_uri = os.getenv("OIDC_INTROSPECTION_ENDPOINT", "")
        Settings.oidc_client_id = os.getenv("OIDC_CLIENT_ID", "sodalite-ide")
        Settings.oidc_client_secret = os.getenv("OIDC_CLIENT_SECRET", "")
        Settings.apiKey = os.getenv("AUTH_API_KEY", "")

        Settings.sql_config = {
            'host': os.getenv('IMAGEBUILDER_DATABASE_URL', 'localhost'),
            'port': int(os.getenv("IMAGEBUILDER_DATABASE_PORT", "5432")),
            'database': os.getenv("IMAGEBUILDER_DATABASE_DB", 'image-builder'),
            'user': os.getenv("IMAGEBUILDER_DATABASE_USER", 'postgres'),
            'password': os.getenv("IMAGEBUILDER_DATABASE_PASSWORD", 'password'),
            'connect_timeout': int(os.getenv("IMAGEBUILDER_DATABASE_TIMEOUT", '3'))
        }

        # prepare sql_config for printing
        __debug_sql_config = copy.deepcopy(Settings.sql_config)
        __debug_sql_config['password'] = '****'

        logger.debug(json.dumps({
            "oicd_config": {
                "introspection_endpoint": Settings.oidc_introspection_endpoint_uri,
                "client_id": Settings.oidc_client_id,
                "client_secret": Settings.oidc_client_secret if Settings.oidc_client_secret == "" else "****",
            },
            "auth_api_key": Settings.apiKey,
            "sql_config": __debug_sql_config,
        }, indent=2))
