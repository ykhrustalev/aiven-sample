from webcheck.repositories import Check, Website, Result
from webcheck.repositories.queries import select


def items_eq(actual, expected):
    assert sorted(expected) == sorted(actual)


def websites_in_db(conn, expected):
    with conn.cursor() as cur:
        actual = select(cur, 'websites', cls=Website, fields=(
            "hostname",
            "id",
        ))
        items_eq(actual, expected)


def checks_in_db(conn, expected):
    with conn.cursor() as cur:
        actual = select(cur, 'checks', cls=Check, fields=(
            "website_id",
            "interval",
            "run_after",
            "expect_http_code",
            "expect_body_pattern",
            "id",
        ))
        items_eq(actual, expected)


def results_in_db(conn, expected):
    with conn.cursor() as cur:
        actual = select(cur, 'results', cls=Result, fields=(
            'check_id',
            'succeed',
            'started_at',
            'duration',
            'http_code',
            'message',
        ), order_by='check_id')
        items_eq(actual, expected)
