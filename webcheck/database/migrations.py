import logging
from collections import namedtuple

from .conn import in_transaction

logger = logging.getLogger(__name__)

Migration = namedtuple('Migration', 'up down')

MIGRATIONS = (
    Migration(
        """
        create table websites(
            id bigserial primary key,
            hostname text unique not null
        );

        create table checks(
            id bigserial primary key,
            website_id bigint,
            interval interval,
            run_after timestamptz,
            expect_http_code int,
            expect_body_pattern text default '',
            constraint fk_website_id
                foreign key(website_id) references websites(id)
                on delete cascade
        );
        create index idx_checks_run_after on checks(run_after);

        create table results(
            check_id bigint not null ,
            succeed boolean not null,
            started_at timestamptz,
            duration interval,
            http_code int not null,
            message text not null default '',
            constraint fk_check_id
                foreign key(check_id) references checks(id)
                on delete cascade
        );
        create index idx_results_started_at on results(started_at);
        """,

        """
        drop table results;
        drop table checks;
        drop table websites;
        """
    ),
)


class Migrator:
    def __init__(self, conn, migrations=MIGRATIONS):
        self.__conn = conn
        self.__migrations = migrations

    def current_version(self):
        with in_transaction(self.__conn) as cur:
            cur.execute('create table if not exists '
                        'migrations(number int primary key)')
            cur.execute('select number from migrations limit 1')
            res = cur.fetchone()
            if not res:
                cur.execute('insert into migrations(number) values (0)')
                version = 0
            else:
                version = int(res[0])

            return version

    def _migrate(self, migrations, current_version, target_version):
        with in_transaction(self.__conn) as cur:
            logger.info("applying migrations starting %d", current_version)
            for migration in migrations:
                cur.execute(migration)

            cur.execute("update migrations set number=%s", (target_version,))
            logger.info("database migrated to %d version", target_version)

    def up(self, step=None):
        current_version = self.current_version()

        if step is None:
            target_version = len(self.__migrations)
        else:
            target_version = current_version + step

        if target_version > len(self.__migrations):
            logger.info("at max available version")
            return

        to_apply = [x.up for x in
                    self.__migrations[current_version:target_version]]
        self._migrate(to_apply, current_version, target_version)

    def down(self, step=None):
        current_version = self.current_version()

        if step is None:
            target_version = 0
        else:
            target_version = current_version - abs(step)

        if target_version < 0:
            logger.info("no to downgrade further")
            return

        to_apply = [x.down for x in self.__migrations[:current_version]]
        to_apply.reverse()

        self._migrate(to_apply, current_version, target_version)
