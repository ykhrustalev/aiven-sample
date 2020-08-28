import logging

import psycopg2

from webcheck import configuration
from webcheck.database.helpers import in_transaction
from webcheck.database.migrations import MIGRATIONS

logger = logging.getLogger(__name__)


def connect(host, port, name, username, password):
    return psycopg2.connect(
        host=host, port=port, database=name, user=username, password=password,
    )


def get_connection(conf: configuration.State):
    return connect(conf.database.host,
                   conf.database.port,
                   conf.database.name,
                   conf.database.username,
                   conf.database.password)


def migrate(conn, migrations=MIGRATIONS):
    with in_transaction(conn) as cur:
        cur.execute('create table if not exists '
                    'migrations(number int primary key)')
        cur.execute('select number from migrations limit 1')
        res = cur.fetchone()
        if not res:
            cur.execute('insert into migrations(number) values (0)')
            index = 0
        else:
            index = int(res[0])

    with in_transaction(conn) as cur:
        logger.info("applying migrations starting %d", index)
        for migration in migrations[index:]:
            cur.execute(migration)

        cur.execute("update migrations set number=%s", (len(migrations),))
        logger.info("database migrated to %d version", len(migrations))
