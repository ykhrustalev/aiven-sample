import logging

import click

from webcheck.repositories import DoesNotExistError
from webcheck.repositories import UniqueConstraintError
from webcheck.repositories import Website
from .app import app, pass_state, run_job, errsay, say
from .state import State
from ..validation import ValidationError

logger = logging.getLogger(__name__)


@app.group(name="websites")
def group():
    pass


@group.command("create")
@click.option('--hostname', help='A hostname to add', required=True)
@pass_state
def create(state: State, hostname):
    def job():
        try:
            obj = state.repo_websites.create(Website(hostname=hostname))
            say(f'created {obj}')
        except UniqueConstraintError:
            errsay('such website already registered')
            return 1
        except ValidationError as e:
            errsay(f'validation error: {e}')
            return 1

    run_job(state, job)


@group.command("delete")
@click.option('--pk', help='A website pk to delete')
@click.option('--hostname', help='A hostname to delete')
@pass_state
def delete(state: State, pk, hostname):
    def job():
        if pk:
            try:
                state.repo_websites.delete_by_id(pk)
            except DoesNotExistError:
                errsay('no such website')
                return 1

            say(f'deleted website pk={pk}')

        if hostname:
            try:
                state.repo_websites.delete_by_hostname(hostname)
            except DoesNotExistError:
                errsay('no such website')
                return 1

            say(f'deleted website hostname={hostname}')

    run_job(state, job)


@group.command("list")
@pass_state
def select(state: State):
    def job():
        for obj in state.repo_websites.list():
            say(obj)

    run_job(state, job)
