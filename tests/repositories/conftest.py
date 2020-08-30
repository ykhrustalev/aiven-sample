from collections import namedtuple
from datetime import timedelta

import pytest

from webcheck.repositories import Results, Result
from webcheck.repositories import Website, Websites, Check, Checks
from webcheck.time import now


@pytest.fixture
def websites_repo(db_conn):
    return Websites(db_conn)


def create_website(repo, hostname):
    return repo.create(Website(hostname=hostname))


@pytest.fixture
def website1(websites_repo):
    yield create_website(websites_repo, 'example1.com')


@pytest.fixture
def website2(websites_repo):
    yield create_website(websites_repo, 'example2.com')


@pytest.fixture
def website3(websites_repo):
    yield create_website(websites_repo, 'example3.com')


@pytest.fixture
def websites_all(website1, website2, website3):
    state = namedtuple('state', 'website1 website2 website3')
    return state(website1, website2, website3)


@pytest.fixture
def checks_repo(db_conn):
    return Checks(db_conn)


def create_check(
    repo,
    website_id,
    interval,
    run_after,
    expect_http_code,
    expect_body_pattern,
):
    return repo.create(Check(
        website_id=website_id,
        interval=interval,
        run_after=run_after,
        expect_http_code=expect_http_code,
        expect_body_pattern=expect_body_pattern,
    ))


@pytest.fixture
def check1a(checks_repo, website1):
    yield create_check(
        checks_repo,
        website_id=website1.id,
        interval=timedelta(seconds=100),
        run_after=now() + timedelta(minutes=5),
        expect_http_code=200,
        expect_body_pattern='',
    )


@pytest.fixture
def check1b(checks_repo, website1):
    yield create_check(
        checks_repo,
        website_id=website1.id,
        interval=timedelta(seconds=200),
        run_after=now() + timedelta(minutes=10),
        expect_http_code=200,
        expect_body_pattern='.*abc.*',
    )


@pytest.fixture
def check2a(checks_repo, website2):
    yield create_check(
        checks_repo,
        website_id=website2.id,
        interval=timedelta(seconds=100),
        run_after=now() + timedelta(minutes=15),
        expect_http_code=400,
        expect_body_pattern='.*foo.*',
    )


@pytest.fixture
def checks_all(check1a, check1b, check2a):
    state = namedtuple('state', 'check1a check1b check2a')
    return state(check1a, check1b, check2a)


@pytest.fixture
def results_repo(db_conn):
    return Results(db_conn)


def create_result(
    repo,
    check_id,
    succeed,
    started_at,
    duration,
    http_code,
    message,
):
    return repo.create(Result(
        check_id=check_id,
        succeed=succeed,
        started_at=started_at,
        duration=duration,
        http_code=http_code,
        message=message,
    ))


@pytest.fixture
def result1a1(results_repo, check1a):
    yield create_result(
        results_repo,
        check_id=check1a.id,
        succeed=True,
        started_at=now() - timedelta(minutes=20),
        duration=timedelta(seconds=10),
        http_code=200,
        message='100',
    )


@pytest.fixture
def result1a2(results_repo, check1a):
    yield create_result(
        results_repo,
        check_id=check1a.id,
        succeed=True,
        started_at=now() - timedelta(minutes=15),
        duration=timedelta(seconds=20),
        http_code=400,
        message='200',
    )


@pytest.fixture
def result1b1(results_repo, check1b):
    yield create_result(
        results_repo,
        check_id=check1b.id,
        succeed=False,
        started_at=now() - timedelta(minutes=10),
        duration=timedelta(seconds=40),
        http_code=-1,
        message='500',
    )


@pytest.fixture
def result2a1(results_repo, check2a):
    yield create_result(
        results_repo,
        check_id=check2a.id,
        succeed=True,
        started_at=now() - timedelta(minutes=5),
        duration=timedelta(seconds=40),
        http_code=200,
        message='400',
    )


@pytest.fixture
def results_all(result1a1, result1a2, result1b1, result2a1):
    state = namedtuple('state', 'result1a1 result1a2 result1b1 result2a1')
    return state(result1a1, result1a2, result1b1, result2a1)
