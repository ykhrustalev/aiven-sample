from datetime import timedelta

import pytest

from webcheck.monitoring import serializers, Task
from webcheck.repositories import Result
from webcheck.time import now


@pytest.mark.parametrize('obj', (
    Task(check_id=1, url='example.com', expect_http_code=0),
    Task(
        check_id=1,
        url='example.com',
        expect_http_code=100,
        expect_body_pattern='xx',
    ),
    Result(
        check_id=1,
        started_at=now(),
        succeed=False,
        duration=timedelta(seconds=5),
        http_code=20,
        message="xx",
    ),
    Result(
        check_id=1,
        started_at=now(),
        succeed=True,
        duration=timedelta(seconds=5),
        http_code=0,
        message="",
    ),
))
def test_pickle(obj):
    s = serializers.Pickle()

    decoded = s.decode(s.encode(obj))
    assert obj == decoded
