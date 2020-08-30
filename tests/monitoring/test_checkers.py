from datetime import timedelta

import pytest
import requests

from webcheck.monitoring import checkers, Task
from webcheck.repositories import Result


@pytest.fixture
def checker():
    yield checkers.HttpChecker(timeout=30, allow_redirects=True)


@pytest.fixture
def url():
    return 'http://host'


@pytest.fixture
def request_get(mocker, url):
    p = mocker.patch('requests.get')
    yield p
    p.assert_called_once_with(url, timeout=30, allow_redirects=True)


@pytest.fixture
def t1(t0):
    return t0 + timedelta(seconds=5)


@pytest.fixture
def thenow(mocker, t0, t1):
    p = mocker.patch('webcheck.monitoring.checkers.now')
    p.side_effect = (t0, t1)
    yield p
    assert p.call_count == 2
    p.assert_has_calls([mocker.call(), mocker.call()])


@pytest.fixture
def resp(mocker, request_get):
    r = mocker.MagicMock()
    r.status_code = 200
    r.text = "response-body"
    request_get.return_value = r
    return r


def test_checker__raises(checker, request_get, thenow, url, t0):
    request_get.side_effect = requests.exceptions.RequestException('foo')

    task = Task(check_id=1,
                url=url,
                expect_http_code=200,
                expect_body_pattern='')

    assert checker.check(task) == Result(
        check_id=1,
        started_at=t0,
        succeed=False,
        duration=timedelta(seconds=5),
        http_code=-1,
        message="exception: foo",
    )


def test_checker__different_code(checker, thenow, url, t0, resp):
    resp.status_code = 400

    task = Task(check_id=1,
                url=url,
                expect_http_code=200,
                expect_body_pattern='')

    assert checker.check(task) == Result(
        check_id=1,
        started_at=t0,
        succeed=False,
        duration=timedelta(seconds=5),
        http_code=400,
        message="invalid status code",
    )


def test_checker__different_pattern(checker, thenow, url, t0, resp):
    task = Task(check_id=1,
                url=url,
                expect_http_code=200,
                expect_body_pattern='xxx')

    assert checker.check(task) == Result(
        check_id=1,
        started_at=t0,
        succeed=False,
        duration=timedelta(seconds=5),
        http_code=200,
        message="body pattern not met",
    )


def test_checker__succeeds_by_code(checker, thenow, url, t0, resp):
    task = Task(check_id=1,
                url=url,
                expect_http_code=200,
                expect_body_pattern='')

    assert checker.check(task) == Result(
        check_id=1,
        started_at=t0,
        succeed=True,
        duration=timedelta(seconds=5),
        http_code=200,
        message="",
    )


def test_checker__succeeds_by_code_and_body(checker, thenow, url, t0, resp):
    task = Task(check_id=1,
                url=url,
                expect_http_code=200,
                expect_body_pattern='.*body.*')

    assert checker.check(task) == Result(
        check_id=1,
        started_at=t0,
        succeed=True,
        duration=timedelta(seconds=5),
        http_code=200,
        message="",
    )
