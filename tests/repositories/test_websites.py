import pytest

from tests.repositories.asserts import items_eq, checks_in_db
from tests.repositories.asserts import websites_in_db
from webcheck.repositories import UniqueConstraintError, DoesNotExistError


def test_create__fails__hostname_uniq(db_conn, websites_repo, website1):
    website1.id += 1
    with pytest.raises(UniqueConstraintError):
        websites_repo.create(website1)


def test_create__succeeds__one(db_conn, websites_repo, website1):
    websites_in_db(db_conn, [website1])


def test_create__succeeds__two(db_conn, websites_repo, website1, website2):
    websites_in_db(db_conn, [website1, website2])


def test_delete_by_pk__fails__missing(db_conn, websites_repo):
    with pytest.raises(DoesNotExistError):
        websites_repo.delete_by_id(100)


def test_delete_by_pk__succeeds(db_conn, websites_repo, website1):
    websites_repo.delete_by_id(website1.id)
    websites_in_db(db_conn, [])


def test_delete_by_hostname__fails__missing(db_conn, websites_repo):
    with pytest.raises(DoesNotExistError):
        websites_repo.delete_by_hostname('something.com')


def test_delete_by_hostname__succeeds(
    db_conn, websites_repo, website1, website2, check1a, check1b, check2a
):
    websites_repo.delete_by_hostname(website1.hostname)
    websites_in_db(db_conn, [website2])
    checks_in_db(db_conn, [check2a])


@pytest.mark.parametrize('filters, expected', (
    (lambda websites_all: {},
     ('website1', 'website2', 'website3',)),
    (lambda websites_all: dict(pks=(websites_all.website1.id,)),
     ('website1',)),
    (lambda websites_all: dict(pks=(websites_all.website1.id,
                                    websites_all.website2.id)),
     ('website1', 'website2',)),
    (lambda websites_all: dict(hostnames=('example1.com',)),
     ('website1',)),
    (lambda websites_all: dict(hostnames=('example1.com', 'example2.com')),
     ('website1', 'website2',)),
))
def test_list__succeeds(
    db_conn, websites_repo, websites_all, filters, expected
):
    actual = websites_repo.list(**filters(websites_all))
    expected = [getattr(websites_all, k) for k in expected]
    items_eq(actual, expected)
