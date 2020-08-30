import abc
import typing
from dataclasses import dataclass, fields, field

import yaml

from webcheck.validation import validate, ValidationError


class Error(Exception):
    pass


class Section(abc.ABC):
    def scheme(self):
        pass

    def allow_unknown(self):
        return False

    def validate(self):
        try:
            validate(self.scheme(), self, allow_unknown=self.allow_unknown())
        except ValidationError as e:
            raise Error(e)


@dataclass(frozen=True)
class Database(Section):
    url: str = ''

    def scheme(self):
        return dict(url=dict(type='string', empty=False))


@dataclass(frozen=True)
class HttpChecker(Section):
    timeout: int = 30
    allow_redirects: bool = True

    def scheme(self):
        return dict(
            timeout=dict(type='integer', min=1),
            allow_redirects=dict(type='boolean'),
        )


@dataclass(frozen=True)
class Kafka(Section):
    servers: typing.List[str]
    topic_checks: str = "monitoring_checks"
    topic_results: str = "monitoring_results"
    producers_options: typing.Dict[str, typing.Any] = \
        field(default_factory=dict)
    consumers_options: typing.Dict[str, typing.Any] = \
        field(default_factory=dict)

    def allow_unknown(self):
        return True

    def scheme(self):
        return dict(
            servers=dict(
                type='list',
                minlength=1,
                required=True,
                schema={'type': 'string'},
            ),
            topic_checks=dict(type='string', empty=False),
            topic_results=dict(type='string', empty=False),
        )


@dataclass(frozen=True)
class Logging(Section):
    destination: typing.Any = None
    level: str = "info"
    format: str = ''

    def scheme(self):
        return dict(
            destination=dict(type='string', nullable=True),
            level=dict(type='string', allowed=['debug', 'info', 'warning']),
            format=dict(type='string', nullable=True),
        )


@dataclass(frozen=True)
class State:
    database: Database
    http_checker: HttpChecker
    kafka: Kafka
    logging: Logging

    def validate(self):
        for section in fields(self):
            sec = getattr(self, section.name)
            sec.validate()


def _load_section(cls, data, name):
    try:
        return cls(**data.get(name, {}))
    except KeyError as e:
        raise Error(
            f"invalid settings in '{name}' section, err: {e}"
        )


def load(path: str) -> State:
    try:
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except IOError as e:
        raise Error(
            f"failed to load a config from {path}, err: {e}"
        )

    if not isinstance(data, dict):
        raise Error("invalid configuration file")

    state = State(
        database=_load_section(Database, data, 'database'),
        kafka=_load_section(Kafka, data, 'kafka'),
        http_checker=_load_section(HttpChecker, data, 'http_checker'),
        logging=_load_section(Logging, data, 'logging'),
    )
    state.validate()

    return state
