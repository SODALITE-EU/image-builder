import datetime
import json
import multiprocessing
import os
import traceback
import uuid
import tempfile
from typing import Optional
from pathlib import Path

from opera.storage import Storage


from image_builder.api.log import get_logger
from image_builder.api.openapi.models import Invocation, InvocationState, BuildParams
from image_builder.api.service import image_builder_service
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

            with tempfile.TemporaryDirectory() as stdstream_dir:
                # stdout&err
                file_stdout = open(InvocationWorkerProcess.stdout_file(stdstream_dir), "w")
                file_stderr = open(InvocationWorkerProcess.stderr_file(stdstream_dir), "w")

                os.dup2(file_stdout.fileno(), 1)
                os.dup2(file_stderr.fileno(), 2)

                inv.state = InvocationState.IN_PROGRESS
                InvocationService.save_invocation(inv)

                try:
                    image_builder_service.build_image(inv)
                    inv.state = InvocationState.SUCCESS
                    # inv.outputs = outputs or None
                except BaseException as e:
                    if isinstance(e, RuntimeError):
                        raise e
                    inv.state = InvocationState.FAILED
                    inv.exception = "{}: {}\n\n{}".format(e.__class__.__name__, str(e), traceback.format_exc())

                file_stdout.flush()
                file_stderr.flush()
                stdout = InvocationWorkerProcess.read_file(InvocationWorkerProcess.stdout_file(stdstream_dir))
                stderr = InvocationWorkerProcess.read_file(InvocationWorkerProcess.stderr_file(stdstream_dir))
                file_stdout.truncate()
                file_stderr.truncate()

                inv.stdout = stdout
                inv.stderr = stderr

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
        inv.job_id = uuid.uuid4()
        inv.build_params = data
        inv.state = InvocationState.PENDING
        inv.timestamp = now.isoformat()
        inv.exception = None
        inv.stdout = None
        inv.stderr = None

        logger.info("ImageBuilding with ID %s at %s", inv.job_id, now.isoformat())

        self.save_invocation(inv)
        self.work_queue.put(inv)
        return inv

    @classmethod
    def load_invocation(cls, job_id: uuid) -> Optional[Invocation]:
        # TODO database
        # try:
        #     inv = SQL_database.get_deployment_status(deployment_id)
        #     # if inv.state == InvocationState.IN_PROGRESS:
        #     #     inv.stdout = InvocationWorkerProcess.read_file(cls.stdout_file(inv.deployment_id))
        #     #     inv.stderr = InvocationWorkerProcess.read_file(cls.stderr_file(inv.deployment_id))
        #     return inv
        #
        # except Exception in (FileNotFoundError, AttributeError):
        #     return None
        storage = Storage.create(".opera-api")
        filename = "invocation-{}.json".format(job_id)
        dump = storage.read_json(filename)
        return Invocation.from_dict(dump)

    @classmethod
    def save_invocation(cls, inv: Invocation):
        # TODO database
        # SQL_database.update_deployment_log(invocation_id, inv)
        storage = Storage.create(".opera-api")
        filename = "invocation-{}.json".format(inv.job_id)
        dump = json.dumps(inv.to_dict(), cls=image_builder_util.UUIDEncoder)
        storage.write(dump, filename)
