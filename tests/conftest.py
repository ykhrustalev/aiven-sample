from os import environ
from urllib.parse import urlparse

import psycopg2
import pytest

from webcheck.database import Migrator

db_url = environ.get('TEST_DATABASE_URL', '')


def reset_db(conn):
    with conn:
        with conn.cursor() as cur:
            parts = urlparse(db_url)
            cur.execute(f'DROP OWNED BY {parts.username};')


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
