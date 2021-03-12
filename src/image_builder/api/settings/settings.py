import json
import os
from pathlib import Path

from image_builder.api.log import get_logger

logger = get_logger(__name__)


class Settings:
    implementation_dir = Path(__file__).absolute().parent.parent
    TOSCA_path = implementation_dir.parent / "TOSCA"

    registry_ip = None

    @staticmethod
    def load_settings():
        Settings.registry_ip = os.getenv("REGISTRY_IP", "localhost")

        logger.debug(json.dumps({
            "registry_ip": Settings.registry_ip
        }, indent=2))
