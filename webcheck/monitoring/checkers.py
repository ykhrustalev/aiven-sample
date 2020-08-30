import abc
import logging
import re

import requests

from webcheck.repositories import Result
from webcheck.time import now
from .models import Task

logger = logging.getLogger(__name__)


class Checker(abc.ABC):
    def check(self, task: Task) -> Result:
        pass


class HttpChecker:
    def __init__(self, timeout: int, allow_redirects=True):
        # assuming redirects are allowed
        self.__timeout = timeout
        self.__allow_redirects = allow_redirects

    def __get(self, url):
        return requests.get(
            url,
            timeout=self.__timeout,
            allow_redirects=self.__allow_redirects,
        )

    def check(self, task: Task) -> Result:
        t0 = now()

        try:
            r = self.__get(task.url)
        except requests.exceptions.RequestException as e:
            return Result(
                check_id=task.check_id,
                started_at=t0,
                duration=now() - t0,
                message=f"exception: {e}",
            )

        state = Result(
            check_id=task.check_id,
            started_at=t0,
            duration=now() - t0,
            http_code=r.status_code,
        )

        reasons = []

        if r.status_code != task.expect_http_code:
            reasons.append('invalid status code')

        if task.expect_body_pattern:
            if not re.match(task.expect_body_pattern, r.text):
                reasons.append('body pattern not met')

        state.succeed = bool(not reasons)
        state.message = ', '.join(reasons)

        return state
