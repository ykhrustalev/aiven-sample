import logging

from webcheck import database
from .app import app, pass_state, run_job

logger = logging.getLogger(__name__)


@app.group()
def db():
    pass


@db.group()
def migrate():
    pass


def get_migrator(state):
    return database.Migrator(state.db_conn)


@migrate.command("up")
@pass_state
def up(state):
    run_job(state, get_migrator(state).up)


@migrate.command("down")
@pass_state
def down(state):
    run_job(state, get_migrator(state).down)
