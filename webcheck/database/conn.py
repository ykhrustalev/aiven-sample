import logging
from contextlib import contextmanager

import psycopg2

logger = logging.getLogger(__name__)


def connect(*args, **kwargs):
    return psycopg2.connect(*args, **kwargs)


@contextmanager
def in_transaction(conn):
    with conn:
        with conn.cursor() as cur:
            yield cur
