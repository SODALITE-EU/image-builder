from image_builder.api.util import image_builder_util
from image_builder.api.openapi.models import Invocation
from pathlib import Path
import pytest
import json
from assertpy import assert_that
import tempfile


class TestUtil:

    def test_mask_workdir(self):
        location = Path("WORKDIR")
        placeholder="$BLUEPRINT_DIR"
        stacktrace = f"{location}/foo/bar"
        masked_trace = image_builder_util.mask_workdir(location, stacktrace, placeholder)
        assert masked_trace == f"{placeholder}/foo/bar"

    def test_uuid_encoder(self, generic_invocation: Invocation):
        with pytest.raises(TypeError):
            string = json.dumps(generic_invocation.to_dict())

        # this should not fail
        string = json.dumps(generic_invocation.to_dict(), cls=image_builder_util.UUIDEncoder)

        assert string is not None

    def test_cwd(self):
        tree = {f'{i}-new.txt': '' for i in range(4)}
        with tempfile.TemporaryDirectory() as workdir:
            for i in range(4):
                (Path(workdir) / f'{i}-new.txt').touch()
            with image_builder_util.cwd(workdir):
                for key in tree.keys():
                    assert_that(str(key)).exists()
