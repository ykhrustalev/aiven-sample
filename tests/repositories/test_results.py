from datetime import timedelta

import pytest

from tests.repositories.asserts import checks_in_db, items_eq
from tests.repositories.asserts import results_in_db
from webcheck.repositories import DoesNotExistError
from webcheck.time import now


def test_create__succeeds__one(db_conn, results_repo, result1a1):
    results_in_db(db_conn, [result1a1])


def test_create__succeeds__two(db_conn, results_repo, result1a1, result1a2):
    results_in_db(db_conn, [result1a1, result1a2])


def test_delete_for_check_id__missing(
    db_conn, results_repo, check1a, check2a
):
    with pytest.raises(DoesNotExistError):
        results_repo.delete_for_check_id(check2a.id + 1)


def test_delete_for_check_id__succeeds(
    db_conn, results_repo, check1a, check2a, result1a1, result1a2, result2a1
):
    results_repo.delete_for_check_id(check1a.id)
    checks_in_db(db_conn, [check1a, check2a])
    results_in_db(db_conn, [result2a1])


@pytest.mark.parametrize('filters, expected', (
    (
        lambda *_: {},
        ('result1a1', 'result1a2', 'result2a1', 'result1b1')
    ),
    (
        lambda checks_all, _: dict(check_ids=(checks_all.check1a.id,)),
        ('result1a1', 'result1a2',)
    ),
    (
        lambda checks_all, _: dict(check_ids=(checks_all.check1a.id,
                                              checks_all.check1b.id)),
        ('result1a1', 'result1a2', 'result1b1')
    ),
    (
        lambda *_: dict(started_at__le=now() - timedelta(minutes=11)),
        ('result1a1', 'result1a2')
    ),
    (
        lambda *_: dict(started_at__ge=now() - timedelta(minutes=9), ),
        ('result2a1',)
    ),
    (
        lambda *_: dict(started_at__le=now() - timedelta(minutes=11),
                        started_at__ge=now() - timedelta(minutes=16), ),
        ('result1a2',)
    ),
))
def test_list__succeeds(db_conn, results_repo, checks_all, results_all,
                        filters, expected):
    actual = results_repo.list(**filters(checks_all, results_all))
    expected = [getattr(results_all, k) for k in expected]
    items_eq(actual, expected)
