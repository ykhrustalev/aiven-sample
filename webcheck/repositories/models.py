from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union


@dataclass(order=True)
class Website:
    hostname: str
    id: int = None


@dataclass(order=True, repr=False)
class Check:
    website_id: int
    interval: timedelta
    expect_http_code: int
    expect_body_pattern: str = ''
    run_after: Union[datetime, None] = None
    id: int = None

    def __repr__(self):
        run_after = (self.run_after.isoformat()
                     if self.run_after
                     else self.run_after)
        return f"Check(website_id={self.website_id}," \
               f" run_after='{run_after}'," \
               f" interval={self.interval}," \
               f" expect_http_code={self.expect_http_code}," \
               f" expect_body_pattern={self.expect_body_pattern}," \
               f" id={self.id}" \
               f")"


@dataclass(order=True, repr=False)
class Result:
    check_id: int
    started_at: datetime
    duration: timedelta
    succeed: bool = False
    http_code: int = -1
    message: str = ""

    def __repr__(self):
        return f"Result(check_id={self.check_id}," \
               f" started_at='{self.started_at.isoformat()}'," \
               f" duration={self.duration}," \
               f" succeed={self.succeed}," \
               f" http_code={self.http_code}," \
               f" message={self.message}" \
               f")"


class Repo:
    def __init__(self, conn):
        self._conn = conn
