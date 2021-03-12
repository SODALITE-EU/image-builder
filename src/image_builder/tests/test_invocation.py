from image_builder.api.service.invocation_service import InvocationService
from image_builder.api.openapi.models import Invocation, BuildParams
import uuid
from assertpy import assert_that


class MockQueue:
    def put(self, inv):
        pass


class MockWorker:
    def __init__(self, arg):
        pass

    def start(self):
        pass


class TestInvocationService:

    def test_save_load_invocation(self, generic_invocation: Invocation):
        inv = generic_invocation
        inv.invocation_id = uuid.uuid4()
        InvocationService.save_invocation(inv)
        inv_new = InvocationService.load_invocation(inv.invocation_id)
        assert_that(inv_new.to_dict()).contains_only(*inv.to_dict().keys())

    def test_invoke(self, mocker, monkeypatch, generic_build_params: BuildParams, generic_invocation: Invocation):

        mocker.patch('multiprocessing.Queue', return_value=None)
        mocker.patch('image_builder.api.service.invocation_service.InvocationService.load_invocation')
        mocker.patch('image_builder.api.service.invocation_service.InvocationWorkerProcess', new=MockWorker)
        inv_service = InvocationService()
        monkeypatch.setattr(inv_service, 'work_queue', MockQueue())

        inv_new = inv_service.invoke(generic_build_params)
        assert_that(inv_new.to_dict()).contains_only(*generic_invocation.to_dict().keys())
