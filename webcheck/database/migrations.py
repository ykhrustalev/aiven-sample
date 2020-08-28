from collections import namedtuple

Migration = namedtuple('Migration', 'up down')

MIGRATIONS = (
    Migration(
        """
        create table websites(
            id bigint primary key,
            hostname text unique not null
        );

        create table checks(
            id bigint primary key,
            website_id bigint,
            interval interval,
            expect_code int,
            constraint fk_website_id
                foreign key(website_id) references websites(id)
        );

        create table results(
            id bigint primary key,
            started_at timestamptz,
            completed_at timestamptz,
            succeed boolean not null,
            http_code int not null default -1,
            message text not null default ''
        );
        create index results_started_at on results(started_at);
        create index results_completed_at on results(completed_at);
        """,

        """
        drop table restrict;
        drop table checks;
        drop table websites;
        """
    ),
)
