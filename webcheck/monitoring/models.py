from dataclasses import dataclass


@dataclass
class Task:
    check_id: int
    url: str
    expect_http_code: int
    expect_body_pattern: str = ''
