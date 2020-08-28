import abc
from dataclasses import dataclass, fields

import typing
import yaml


class Section(abc.ABC):
    def validate(self):
        pass


class Error(Exception):
    pass


@dataclass(frozen=True)
class Database(Section):
    host: str
    name: str
    username: str
    password: str
    port: int = 5432

    def validate(self):
        if not self.host:
            raise Error("'host' should be set")

        if not self.name:
            raise Error("'name' should be set")

        if not self.username:
            raise Error("'username' should be set")

        try:
            int(self.port)
        except ValueError:
            raise Error("'port' should be int")


@dataclass(frozen=True)
class Logging(Section):
    destination: typing.Any = None
    level: str = "info"

    ALLOWED_LEVELS = ('debug', 'info', 'warning')

    def validate(self):
        if self.level not in self.ALLOWED_LEVELS:
            raise Error(f"'level' should be in {self.ALLOWED_LEVELS}")


@dataclass(frozen=True)
class State(Section):
    database: Database
    logging: Logging

    def validate(self):
        for section in fields(self):
            getattr(self, section.name).validate()


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
        logging=_load_section(Logging, data, 'logging')
    )
    state.validate()

    return state
