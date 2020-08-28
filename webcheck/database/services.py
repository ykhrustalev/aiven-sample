from psycopg2 import errors

from file_appliance.database.models import Account
from .errors import DoesNotExistError, UniqueConstraintError
from .utils import in_transaction


class Accounts:
    object_names = (
        'property_id',
        'name',
        'path',
        'property_deleted',
        'property_deleted_on',
        'contents_parked',
        'contents_parked_on',
    )

    def __init__(self, conn):
        self.conn = conn

    def _row_to_object(self, row):
        return Account(**dict(zip(self.object_names, row)))

    def insert(self, account):
        with in_transaction(self.conn) as cur:
            data = {
                "property_id": account.property_id,
                "name": account.name,
                "path": account.path,
                "property_deleted": account.property_deleted,
                "property_deleted_on": account.property_deleted_on,
                "contents_parked": account.contents_parked,
                "contents_parked_on": account.contents_parked_on,
            }

            query = """
            insert into accounts(
                property_id,
                name,
                path,
                property_deleted,
                property_deleted_on,
                contents_parked,
                contents_parked_on
            )
            values (
                %(property_id)s,
                %(name)s,
                %(path)s,
                %(property_deleted)s,
                %(property_deleted_on)s,
                %(contents_parked)s,
                %(contents_parked_on)s
            )
            """
            try:
                cur.execute(query, data)
            except errors.UniqueViolation:
                raise UniqueConstraintError()

        return Account(**data)

    def update_one(self, property_id, account):
        with in_transaction(self.conn) as cur:
            data = {
                "property_id": property_id,
                "name": account.name,
                "path": account.path,
                "property_deleted": account.property_deleted,
                "property_deleted_on": account.property_deleted_on,
                "contents_parked": account.contents_parked,
                "contents_parked_on": account.contents_parked_on,
            }

            query = """
            update accounts
            set
                name=%(name)s,
                path=%(path)s,
                property_deleted=%(property_deleted)s,
                property_deleted_on=%(property_deleted_on)s,
                contents_parked=%(contents_parked)s,
                contents_parked_on=%(contents_parked_on)s
            where property_id=%(property_id)s
            """
            cur.execute(query, data)
            cnt = cur.rowcount

        if cnt != 1:
            raise DoesNotExistError()

    def delete_one(self, property_id):
        with in_transaction(self.conn) as cur:
            query = """
            delete from accounts
            where property_id=%s
            """
            cur.execute(query, [property_id])
            cnt = cur.rowcount

        if cnt != 1:
            raise DoesNotExistError()

    def list(self, property_ids=None, name=None, property_deleted=None,
             contents_parked=None):
        with in_transaction(self.conn) as cur:
            query = """
            select
                property_id,
                name,
                path,
                property_deleted,
                property_deleted_on,
                contents_parked,
                contents_parked_on
            from accounts
            where {conditions}
            order by name, property_id
            """

            conditions = '1=1'
            args = {}

            if property_ids:
                conditions += ' and property_id in %(property_ids)s'
                args['property_ids'] = tuple(property_ids)
            if name is not None:
                conditions += ' and name=%(name)s'
                args['name'] = name
            if property_deleted is not None:
                conditions += ' and property_deleted=%(property_deleted)s'
                args['property_deleted'] = property_deleted
            if contents_parked is not None:
                conditions += ' and contents_parked=%(contents_parked)s'
                args['contents_parked'] = contents_parked

            query = query.format(conditions=conditions)
            cur.execute(query, args)

            def walk():
                for row in cur.fetchall():
                    yield Account(**dict(zip(self.object_names, row)))

            return list(walk())
