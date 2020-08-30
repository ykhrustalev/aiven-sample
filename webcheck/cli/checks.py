import logging
from datetime import timedelta

import click

from webcheck.repositories import DoesNotExistError, Check
from .app import app, pass_state, run_job, errsay, say
from .state import State
from ..validation import ValidationError

logger = logging.getLogger(__name__)


@app.group(name="checks")
def group():
    pass


@group.command("create")
@click.option('--website-id', type=int, required=True,
              help='A website to attach check')
@click.option('--interval', type=int, required=True,
              help='An interval in seconds')
@click.option('--expect-http-code', type=int, required=True,
              help='An http code to expect', default=200)
@click.option('--expect-body-pattern',
              help='A body pattern to expect', default='')
@pass_state
def create(
    state: State,
    website_id,
    interval,
    expect_http_code,
    expect_body_pattern,
):
    repo = state.repo_checks

    def job():
        obj = Check(
            website_id=website_id,
            interval=timedelta(seconds=interval),
            run_after=None,
            expect_http_code=expect_http_code,
            expect_body_pattern=expect_body_pattern,
        )
        try:
            obj = repo.create(obj)
            say(f'created {obj}')
        except DoesNotExistError:
            errsay("referenced website doesn't exist")
            return 1
        except ValidationError as e:
            errsay(f'validation error: {e}')
            return 1

    run_job(state, job)


@group.command("delete")
@click.option('--pk', help='An check pk filter')
@click.option('--website-id', help='A website id filter')
@pass_state
def delete(state: State, pk, website_id):
    def job():
        repo = state.repo_checks

        if pk:
            try:
                repo.delete_by_id(pk)
                say('deleted checks')
            except DoesNotExistError:
                errsay(f'no such check {pk}')
                return 1

        if website_id:
            try:
                repo.delete_for_website_id(website_id)
                say('deleted checks')
            except DoesNotExistError:
                errsay(f'no checks for {website_id}')
                return 1

    run_job(state, job)


@group.command("list")
@click.option('--website-id', help='A website id filter')
@pass_state
def select(state: State, website_id):
    def job():
        filters = {}

        if website_id:
            filters['website_ids'] = [website_id]

        for obj in state.repo_checks.list(**filters):
            say(obj)

    run_job(state, job)
