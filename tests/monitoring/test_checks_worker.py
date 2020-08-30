import pytest

from webcheck.monitoring import ChecksWorker, Task


@pytest.fixture
def checker(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def task1():
    return Task(
        check_id=100,
        url='https://example1.com',
        expect_http_code=200,
        expect_body_pattern='xx',
    )


@pytest.fixture
def task2():
    return Task(
        check_id=200,
        url='https://example2.com',
        expect_http_code=400,
        expect_body_pattern='',
    )


@pytest.fixture
def task3():
    return Task(
        check_id=300,
        url='https://example3.com',
        expect_http_code=204,
        expect_body_pattern='',
    )


def test_execute(
    mocker,
    checker,
    consumer,
    producer,
    task1, task2,
    result1, result3,
):
    worker = ChecksWorker(checker, consumer, producer)

    consumer.receive.return_value = [task1, task2, task3]
    checker.check.side_effect = (result1, Exception('foo'), result3)

    worker.execute()

    consumer.receive.assert_called_once_with()

    assert 3 == checker.check.call_count
    checker.check.assert_has_calls([
        mocker.call(task1),
        mocker.call(task2),
        mocker.call(task3),
    ])

    assert 2 == producer.send.call_count
    producer.send.assert_has_calls([
        mocker.call(result1),
        mocker.call(result3),
    ])
    assert 2 == producer.flush.call_count
    producer.flush.assert_has_calls([
        mocker.call(),
        mocker.call(),
    ])
