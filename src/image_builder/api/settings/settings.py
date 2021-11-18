import json
import os
from pathlib import Path

from image_builder.api.log import get_logger

logger = get_logger(__name__)


class Settings:
    implementation_dir = Path(__file__).absolute().parent.parent
    TOSCA_path = implementation_dir.parent / "TOSCA"

    registry_ip = None

    # Authorization and Authentication config
    oidc_introspection_endpoint_uri = None
    oidc_client_id = None
    oidc_client_secret = None
    apiKey = None
    connection_protocols = ["http://", "https://"]

    @staticmethod
    def load_settings():
        Settings.registry_ip = os.getenv("REGISTRY_IP", "localhost")

        Settings.oidc_introspection_endpoint_uri = os.getenv("OIDC_INTROSPECTION_ENDPOINT", "")
        Settings.oidc_client_id = os.getenv("OIDC_CLIENT_ID", "sodalite-ide")
        Settings.oidc_client_secret = os.getenv("OIDC_CLIENT_SECRET", "")
        Settings.apiKey = os.getenv("AUTH_API_KEY", "")

        logger.debug(json.dumps({
            "registry_ip": Settings.registry_ip,
            "oicd_config": {
                "introspection_endpoint": Settings.oidc_introspection_endpoint_uri,
                "client_id": Settings.oidc_client_id,
                "client_secret": Settings.oidc_client_secret,
            },
            "auth_api_key": Settings.apiKey,
        }, indent=2))
