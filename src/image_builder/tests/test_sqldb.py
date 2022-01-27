import datetime
import json
import logging
import uuid

import psycopg2
from assertpy import assert_that
import pytest

from image_builder.api.openapi.models import InvocationState, Invocation
from image_builder.api.openapi.models.base_model_ import Model as BaseModel
from image_builder.api.service.sqldb_service import PostgreSQL, SqlDBFailedException



class FakePostgres:
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def cursor():
        return NoneCursor()

    def commit(self):
        pass

    def close(self):
        pass


# Class to be redefined with custom fetchone or fetchall function
class NoneCursor:
    command = ""
    replacements = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def execute(cls, command, replacements=None):
        if isinstance(command, psycopg2.sql.Composed):
            cls.command = command._wrapped.__repr__()
        else:
            cls.command = command
        cls.replacements = replacements
        return None

    @classmethod
    def fetchone(cls):
        return None

    @classmethod
    def fetchall(cls):
        return []

    @classmethod
    def close(cls):
        pass

    @classmethod
    def get_command(cls):
        """This method does not exist in real Cursor object, for testing purposes only"""
        return cls.command

    @classmethod
    def get_replacements(cls):
        """This method does not exist in real Cursor object, for testing purposes only"""
        return cls.replacements


class PsycopgErrorCursor(NoneCursor):

    @classmethod
    def execute(cls, command, replacements=None):
        if command != "ROLLBACK":
            raise psycopg2.Error
        return None

class GetInvocationCursor(NoneCursor):

    @classmethod
    def fetchone(cls):
        return [json.dumps(x) for x in TestBuildStatus.invocations]


class TestConnection:
    def test_psycopg2_error(self, mocker):
        mocker.patch('psycopg2.connect', side_effect=psycopg2.Error)
        with pytest.raises(SqlDBFailedException):
            # PostgreSQL.connection() is a contextmanager
            with PostgreSQL.connection():
                pass

    def test_psycopg2_success(self, mocker):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        with PostgreSQL.connection():
            pass

    def test_cursor(self, mocker):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        with PostgreSQL.cursor():
            pass

    def test_execute(self, mocker):
        command = "foo bar"
        mocker.patch('psycopg2.connect', new=FakePostgres)
        assert PostgreSQL.execute(command=command)
        assert NoneCursor.get_command() == command

    def test_execute_error(self, mocker, monkeypatch):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        monkeypatch.setattr(FakePostgres, 'cursor', PsycopgErrorCursor)
        assert not PostgreSQL.execute(command='foo')

    def test_initialize(self, mocker):
        mock_execute = mocker.MagicMock(name='execute')
        mocker.patch('image_builder.api.service.sqldb_service.PostgreSQL.execute', new=mock_execute)
        PostgreSQL.initialize()
        assert mock_execute.call_count == 1


class TestBuildStatus:
    invocations = [
        {
            'invocation_id': 'a293c356-b87c-438b-9faf-dacf78ced6a0',
            'build_params': {
                "source": {
                    "git_repo": {
                        "url": "https://gitlab.com/wds-co/SnowWatch-SODALITE.git"
                    }
                },
                "target": {
                    "images": [
                        {
                            "image": "xopera-rest-api",
                            "tag": "latest"
                        }
                    ],
                    "registry": {
                        "url": "localhost:5000"
                    }
                }
            },
            'state': InvocationState.PENDING,
            'timestamp_submission': datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            'response': None

        }
    ]

    def test_update(self, mocker, monkeypatch, generic_invocation):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        db = PostgreSQL()
        assert db.update_build_status(generic_invocation)
        assert_that(NoneCursor.get_replacements()).contains(str(generic_invocation.invocation_id))

    def test_update_fail(self, mocker, monkeypatch, generic_invocation):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        db = PostgreSQL()
        monkeypatch.setattr(FakePostgres, 'cursor', PsycopgErrorCursor)
        assert not db.update_build_status(generic_invocation)

    def test_get_none(self, mocker, monkeypatch, generic_invocation):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        db = PostgreSQL()
        assert not db.get_build_status(uuid.uuid4())

    def test_get(self, mocker, monkeypatch):
        mocker.patch('psycopg2.connect', new=FakePostgres)
        db = PostgreSQL()
        monkeypatch.setattr(FakePostgres, 'cursor', GetInvocationCursor)
        inv = db.get_build_status(uuid.uuid4())
        assert_that(inv).is_equal_to(Invocation.from_dict(TestBuildStatus.invocations[0]))
