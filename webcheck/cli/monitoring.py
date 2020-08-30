import logging
import time

import click

from .app import app, pass_state, run_job
from .state import State

logger = logging.getLogger(__name__)


@app.group(name="monitoring")
def group():
    pass


@group.command("scheduler")
@click.option('--interval', type=int, default=20,
              help='A check interval in seconds')
@pass_state
def scheduler(state: State, interval):
    def job():
        while True:
            state.monitoring_scheduler.schedule()
            time.sleep(interval)

    run_job(state, job)


@group.command("checks_worker")
@pass_state
def checks_worker(state: State):
    run_job(state, lambda: state.monitoring_checks_worker.execute())


@group.command("results_worker")
@pass_state
def results_worker(state: State):
    run_job(state, lambda: state.monitoring_results_worker.execute())
