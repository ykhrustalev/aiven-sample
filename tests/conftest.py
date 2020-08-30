from os import environ

import psycopg2
import pytest

from webcheck.database import Migrator

db_url = environ.get('TEST_DATABASE_URL', '')


def reset_db(conn):
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            drop table if exists migrations;
            drop table if exists results;
            drop table if exists checks;
            drop table if exists websites;
            """)


@pytest.fixture
def db_clean_conn():
    conn = psycopg2.connect(db_url)

    reset_db(conn)

    yield conn

    reset_db(conn)
    conn.close()


@pytest.fixture
def db_conn(db_clean_conn):
    Migrator(db_clean_conn).up()
    yield db_clean_conn
