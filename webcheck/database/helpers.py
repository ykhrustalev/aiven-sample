from contextlib import contextmanager


@contextmanager
def in_transaction(conn):
    with conn:
        with conn.cursor() as cur:
            yield cur
