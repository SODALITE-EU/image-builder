import json
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID


@contextmanager
def cwd(path):
    old_pwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_pwd)


def mask_workdir(location: Path, stacktrace: str, placeholder="$BLUEPRINT_DIR"):
    """
    replaces real workdir with placeholder
    """
    return stacktrace.replace(str(location), placeholder)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)
