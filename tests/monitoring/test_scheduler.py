from dataclasses import replace
from datetime import timedelta, datetime

import pytest

from webcheck.monitoring import Scheduler, Task
from webcheck.repositories import Check, Website


@pytest.fixture
def thenow(mocker, t0):
    p = mocker.patch('webcheck.monitoring.scheduler.now')
    p.side_effect = (t0, t0, t0)
    yield p
    p.assert_has_calls([
        mocker.call(),
        mocker.call(),
        mocker.call(),
    ])


@pytest.fixture
def website1():
    return Website(id=10, hostname="example1.com")


@pytest.fixture
def website2():
    return Website(id=20, hostname="example2.com")


@pytest.fixture
def check1():
    return Check(
        website_id=10,
        interval=timedelta(minutes=5),
        expect_http_code=200,
        run_after=datetime.now() - timedelta(minutes=1),
        id=100,
    )


@pytest.fixture
def check2():
    return Check(
        website_id=20,
        interval=timedelta(minutes=4),
        expect_http_code=200,
        expect_body_pattern='xxx',
        run_after=datetime.now() - timedelta(minutes=2),
        id=200,
    )


@pytest.fixture
def check3():
    return Check(
        website_id=30,
        interval=timedelta(minutes=5),
        expect_http_code=400,
        run_after=datetime.now() - timedelta(minutes=3),
        id=300,
    )


def test_execute(
    mocker,
    producer,
    repo_websites, repo_checks,
    t0, thenow,
    website1, website2,
    check1, check2, check3,
):
    scheduler = Scheduler(repo_websites, repo_checks, producer)

    repo_checks.list.return_value = [check1, check2, check3]
    repo_websites.list.return_value = [website1, website2]

    scheduler.schedule()

    repo_checks.list.assert_called_once_with(run_after__le=t0)

    assert 2 == repo_checks.update.call_count
    repo_checks.update.assert_has_calls([
        mocker.call(replace(check1, run_after=t0 + check1.interval)),
        mocker.call(replace(check2, run_after=t0 + check2.interval)),
    ])

    repo_websites.list.assert_called_once_with(
        pks=[check1.website_id,
             check2.website_id,
             check3.website_id]
    )

    assert 2 == producer.send.call_count
    producer.send.assert_has_calls([
        mocker.call(Task(
            check_id=100,
            url=f'https://{website1.hostname}',
            expect_http_code=check1.expect_http_code,
            expect_body_pattern=check1.expect_body_pattern,
        )),
        mocker.call(Task(
            check_id=200,
            url=f'https://{website2.hostname}',
            expect_http_code=check2.expect_http_code,
            expect_body_pattern=check2.expect_body_pattern,
        )),
    ])
    producer.flush.assert_called_once_with()
