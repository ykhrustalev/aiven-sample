import logging

from .app import app, pass_state, run_job

logger = logging.getLogger(__name__)


@app.group()
def db():
    pass


@db.group()
def migrate():
    pass


@migrate.command("up")
@pass_state
def up(state):
    run_job(state, state.migrator.up)


@migrate.command("down")
@pass_state
def down(state):
    run_job(state, state.migrator.down)
