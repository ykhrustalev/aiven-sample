import logging

from psycopg2.errors import UniqueViolation

from .errors import DoesNotExistError, UniqueConstraintError

logger = logging.getLogger(__name__)


def to_csv(fields):
    return ', '.join(fields)


def to_placeholders(fields):
    return ', '.join([f'%({x})s' for x in fields])


def exists(cur, table, conditions, args):
    cur.execute(f'select count(*) from {table} where {conditions}', args)
    return 0 != cur.fetchone()[0]


def is_unique(cur, table, conditions, args):
    if exists(cur, table, conditions, args):
        raise UniqueConstraintError('object is not unique')


def insert(cur, table, fields, args, returning='returning id'):
    query = f"""
            insert into {table}({to_csv(fields)})
            values ({to_placeholders(fields)})
            {returning}
            """
    try:
        cur.execute(query, args)
        return cur.fetchone()[0]
    except UniqueViolation:
        raise UniqueConstraintError(
            'the record conflicts with the existing one'
        )


def to_update_pairs(fields):
    return ', '.join(f'{x}=%({x})s' for x in fields)


def update(cur, table, fields, conditions, args):
    query = f"""
            update {table}
            set {to_update_pairs(fields)}
            where ({conditions})
            """
    cur.execute(query, args)


def delete(cur, table, args, conditions='id=%s'):
    cur.execute(f"delete from {table} where {conditions}", args)
    if cur.rowcount == 0:
        raise DoesNotExistError('no objects match the condition')


def select(cur, table, cls=dict, fields=(), conditions='1=1', args=(),
           order_by='id'):
    query = f"""
            select {to_csv(fields)}
            from {table}
            where {conditions}
            order by {order_by}
            """
    cur.execute(query, args)

    def walk():
        for row in cur.fetchall():
            yield cls(**dict(zip(fields, row)))

    return list(walk())
