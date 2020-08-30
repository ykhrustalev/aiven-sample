import dataclasses
from datetime import timedelta

import pytest

from tests.repositories.asserts import checks_in_db, items_eq, websites_in_db
from webcheck.repositories import DoesNotExistError
from webcheck.time import now


def test_create__succeeds__one(db_conn, checks_repo, check1a):
    checks_in_db(db_conn, [check1a])


def test_create__succeeds__two(db_conn, checks_repo, check1a, check2a):
    checks_in_db(db_conn, [check1a, check2a])


def test_update__succeeds(db_conn, checks_repo, check1a, check2a, website2):
    copy = dataclasses.replace(
        check1a,
        website_id=website2.id,
        interval=timedelta(seconds=50),
        run_after=now() + timedelta(minutes=99),
        expect_http_code=204,
        expect_body_pattern='xx',
    )

    checks_repo.update(copy)
    checks_in_db(db_conn, [copy, check2a])


def test_delete_by_pk__fails__missing(db_conn, checks_repo):
    with pytest.raises(DoesNotExistError):
        checks_repo.delete_by_id(100)


def test_delete_by_pk__succeeds(db_conn, checks_repo, check1a, check1b):
    checks_repo.delete_by_id(check1a.id)
    checks_in_db(db_conn, [check1b])


def test_delete_for_website__fails__missing(db_conn, checks_repo):
    with pytest.raises(DoesNotExistError):
        checks_repo.delete_for_website_id(-1)


def test_delete_for_website__succeeds(
    db_conn, checks_repo, website1, website2, checks_all, check2a,
):
    checks_repo.delete_for_website_id(website1.id)
    websites_in_db(db_conn, [website1, website2])
    checks_in_db(db_conn, [check2a])


@pytest.mark.parametrize('filters, expected', (
    (
        lambda *_: {},
        ('check1a', 'check1b', 'check2a',)
    ),
    (
        lambda _, checks_all: dict(pks=(checks_all.check1a.id,)),
        ('check1a',)
    ),
    (
        lambda _, checks_all: dict(pks=(checks_all.check1a.id,
                                        checks_all.check1b.id)),
        ('check1a', 'check1b',)
    ),
    (
        lambda websites_all, _: dict(website_ids=(websites_all.website1.id,)),
        ('check1a', 'check1b')
    ),
    (
        lambda websites_all, _: dict(website_ids=(websites_all.website2.id,)),
        ('check2a',)
    ),
    (
        lambda websites_all, _: dict(website_ids=(websites_all.website3.id,)),
        ()
    ),
    (
        lambda *_: dict(run_after__le=now() + timedelta(minutes=6)),
        ('check1a',)
    ),
    (
        lambda *_: dict(run_after__le=now() + timedelta(minutes=11)),
        ('check1a', 'check1b')
    ),
    (
        lambda *_: dict(run_after__le=now()),
        ()
    ),
))
def test_list__succeeds(db_conn, checks_repo, websites_all, checks_all,
                        filters, expected):
    actual = checks_repo.list(**filters(websites_all, checks_all))
    expected = [getattr(checks_all, k) for k in expected]
    items_eq(actual, expected)
