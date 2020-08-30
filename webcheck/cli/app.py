import logging
import os
import sys

import click

from webcheck import configuration
from .logging import setup_logging
from .state import State

# do not fail on missing explicit locale
# https://github.com/pallets/click/issues/448#issuecomment-246029304
click.core._verify_python3_env = lambda: None

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = '/etc/webcheck/config.yaml'


def say(msg):
    print(msg)


def errsay(msg):
    sys.stderr.write(msg)
    sys.stderr.write('\n')


def run_job(state: State, job):
    """Run the job and exit, allows doing it with locking

    :param state: the cli state
    :param job: an executable to run
    """
    rc = 1
    try:
        setup(state)
        rc = job()
        # in case exit code is not defined
        if rc is None:
            rc = 0
    except Exception:
        logger.exception('unexpected error')

    sys.exit(rc)


pass_state = click.make_pass_decorator(State, ensure=True)


def setup(state: State):
    setup_logging(
        file_path=state.config.logging.destination,
        fmt=state.config.logging.format,
        level=state.config.logging.level,
        print_console=state.print_console,
    )


def config_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.config = configuration.load(value)
        return value

    return click.option(
        '-c', '--config',
        default=lambda: os.environ.get('WEBCHECK_CONFIG', DEFAULT_CONFIG_FILE),
        expose_value=False,
        help='Configuration file to use',
        callback=callback
    )(f)


def silent_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.print_console = not value
        return value

    return click.option(
        '-s', '--silent',
        default=False,
        is_flag=True,
        expose_value=False,
        help='Do not log to stdout',
        callback=callback
    )(f)


def common_options(f):
    f = config_option(f)
    f = silent_option(f)
    return f


@click.group()
@common_options
def app():
    pass
