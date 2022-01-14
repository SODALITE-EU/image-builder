import json
import uuid

import psycopg2
from psycopg2 import sql
from contextlib import contextmanager

from image_builder.api.log import get_logger
from image_builder.api.openapi.models import Invocation
from image_builder.api.settings import Settings
from image_builder.api.util.image_builder_util import UUIDEncoder

logger = get_logger(__name__)


class SqlDBFailedException(Exception):
    pass


class PostgreSQL:

    @classmethod
    @contextmanager
    def connection(cls):
        try:
            conn = psycopg2.connect(**Settings.sql_config)
            yield conn
            conn.close()
        except psycopg2.Error as e:
            logger.error(f"Error while connecting to PostgreSQL: {str(e)}")
            raise SqlDBFailedException('Could not connect to PostgreSQL DB')

    @classmethod
    @contextmanager
    def cursor(cls):
        with cls.connection() as conn:
            yield conn.cursor()

    @classmethod
    def execute(cls, command, replacements=None):

        with cls.connection() as conn:
            dbcur = conn.cursor()
            try:
                if replacements is not None:
                    dbcur.execute(command, replacements)
                else:
                    dbcur.execute(command)
                conn.commit()
            except psycopg2.Error as e:
                logger.debug(str(e))
                dbcur.execute("ROLLBACK")
                conn.commit()
                return False

        return True

    @classmethod
    def initialize(cls):

        cls.execute("""
                        create table if not exists {} (
                        invocation_id varchar (36),
                        state varchar(36),
                        timestamp timestamp, 
                        _log text,  
                        primary key (invocation_id)
                        );""".format(Settings.invocation_table))

    @classmethod
    def update_build_status(cls, inv: Invocation):
        """
        updates building log with invocation
        """

        response = cls.execute(
            """insert into {} (invocation_id, state, timestamp, _log)
               values (%s, %s, %s, %s)
               ON CONFLICT (invocation_id) DO UPDATE
                   SET timestamp=excluded.timestamp,
                       state=excluded.state,
                        _log=excluded._log;"""
                .format(Settings.invocation_table),
            (str(inv.invocation_id), inv.state, str(inv.timestamp_submission), json.dumps(inv.to_dict(), cls=UUIDEncoder)))
        if response:
            logger.debug(
                f'Updated building log for invocation_id={inv.invocation_id} in PostgreSQL database')
        else:
            logger.error(
                f'Failed to update building log for  invocation_id={inv.invocation_id} in PostgreSQL database')
        return response

    @classmethod
    def get_build_status(cls, invocation_id: uuid):
        """
        Get last building log
        """

        with cls.cursor() as dbcur:
            stmt = sql.SQL("""select _log from {invocation_table} 
                                where invocation_id = {invocation_id};""").format(
                invocation_table=sql.Identifier(Settings.invocation_table),
                invocation_id=sql.Literal(str(invocation_id))
            )

            dbcur.execute(stmt)
            line = dbcur.fetchone()
            if not line:
                return None
            inv = Invocation.from_dict(json.loads(line[0]))

            return inv
