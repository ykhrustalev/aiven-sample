from datetime import datetime, timedelta

import pytest

from webcheck.repositories import Result


@pytest.fixture
def t0():
    return datetime.now() - timedelta(seconds=30)


@pytest.fixture
def producer(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def consumer(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def repo_websites(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def repo_checks(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def repo_results(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def result1():
    return Result(
        check_id=100,
        started_at=datetime.utcnow(),
        duration=timedelta(seconds=10),
    )


@pytest.fixture
def result2():
    return Result(
        check_id=200,
        started_at=datetime.utcnow(),
        duration=timedelta(seconds=10),
    )


@pytest.fixture
def result3():
    return Result(
        check_id=300,
        started_at=datetime.utcnow(),
        duration=timedelta(seconds=20),
    )
