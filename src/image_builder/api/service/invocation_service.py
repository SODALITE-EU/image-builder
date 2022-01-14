import datetime
import json
import multiprocessing
import os
import tempfile
import traceback
import uuid
import sys
from pathlib import Path
from typing import Optional

from opera.storage import Storage

from image_builder.api.log import get_logger
from image_builder.api.openapi.models import Invocation, InvocationState, BuildParams
from image_builder.api.service import image_builder_service
from image_builder.api.service.sqldb_service import PostgreSQL
from image_builder.api.util import image_builder_util


logger = get_logger(__name__)


class InvocationWorkerProcess(multiprocessing.Process):

    def __init__(self, work_queue: multiprocessing.Queue):
        super(InvocationWorkerProcess, self).__init__(
            group=None, target=self._run_internal, name="Invocation-Worker", args=(),
            kwargs={
                "work_queue": work_queue,
            }, daemon=None)

    @staticmethod
    def _run_internal(work_queue: multiprocessing.Queue):

        while True:
            inv: Invocation = work_queue.get(block=True)
            inv.timestamp_start = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

            with tempfile.TemporaryDirectory() as stdstream_dir:
                # stdout
                file_stdout = open(InvocationWorkerProcess.stdout_file(stdstream_dir), "w")

                os.dup2(file_stdout.fileno(), 1)

                inv.state = InvocationState.IN_PROGRESS
                InvocationService.save_invocation(inv)

                try:
                    image_builder_service.build_image(inv)
                    inv.state = InvocationState.SUCCESS
                except BaseException as e:
                    if isinstance(e, RuntimeError):
                        raise e
                    inv.state = InvocationState.FAILED

                    logger.exception("{}: {}\n\n{}".format(e.__class__.__name__, str(e), traceback.format_exc()))

                sys.stdout.flush()
                inv.response = InvocationWorkerProcess.read_file(InvocationWorkerProcess.stdout_file(stdstream_dir))
                file_stdout.close()

                inv.timestamp_end = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

                InvocationService.save_invocation(inv)

    @staticmethod
    def read_file(filename):
        with open(filename, "r") as f:
            return f.read()

    @staticmethod
    def stdout_file(workdir: Path):
        return Path(workdir) / "stdout.txt"

    @staticmethod
    def stderr_file(workdir: Path):
        return Path(workdir) / "stderr.txt"


class InvocationService:

    def __init__(self):
        self.work_queue: multiprocessing.Queue = multiprocessing.Queue()
        self.worker = InvocationWorkerProcess(self.work_queue)
        self.worker.start()

    def invoke(self, data: BuildParams):

        now = datetime.datetime.now(tz=datetime.timezone.utc)

        inv = Invocation()
        inv.invocation_id = uuid.uuid4()
        inv.build_params = data
        inv.state = InvocationState.PENDING
        inv.timestamp_submission = now.isoformat()
        inv.response = None

        logger.info("ImageBuilding with ID %s at %s", inv.invocation_id, now.isoformat())

        self.save_invocation(inv)
        self.work_queue.put(inv)
        return inv

    @classmethod
    def load_invocation(cls, job_id: uuid) -> Optional[Invocation]:
        inv = PostgreSQL.get_build_status(job_id)
        return inv

    @classmethod
    def save_invocation(cls, inv: Invocation):
        PostgreSQL.update_build_status(inv)
