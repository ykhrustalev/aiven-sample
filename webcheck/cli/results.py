import logging

import click

from webcheck.repositories import DoesNotExistError
from .app import app, pass_state, run_job, errsay, say
from .state import State

logger = logging.getLogger(__name__)


@app.group(name="results")
def group():
    pass


@group.command("delete")
@click.option('--check-id', help='A check id filter')
@pass_state
def delete(state: State, check_id):
    def job():
        if check_id:
            try:
                state.repo_results.delete_for_check_id(check_id)
                say('deleted checks')
            except DoesNotExistError:
                errsay(f'no check with id={check_id}')
                return 1

    run_job(state, job)


@group.command("list")
@click.option('--check-id', help='A check id filter')
@click.option('--since', help='from filter')
@click.option('--until', help='to filter')
@pass_state
def select(state: State, check_id, since, until):
    def job():
        filters = {}

        if check_id:
            filters['check_ids'] = [check_id]

        if since:
            filters['started_at__ge'] = since

        if until:
            filters['started_at__le'] = until

        for obj in state.repo_results.list(**filters, order_by='started_at'):
            say(obj)

    run_job(state, job)
