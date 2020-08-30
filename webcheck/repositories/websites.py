from dataclasses import asdict
from typing import List

from webcheck.database import in_transaction
from webcheck.validation import validate
from .models import Repo, Website
from .queries import is_unique, insert, delete, select

scheme_create = dict(
    id=dict(type='integer', nullable=True),
    hostname=dict(type='string', regex=r'^[a-zA-Z0-9_\.+-]+$')
)


class Websites(Repo):
    def create(self, obj: Website) -> Website:
        validate(scheme_create, obj)

        with in_transaction(self._conn) as cur:
            is_unique(cur, 'websites', 'hostname = %s', [obj.hostname])

            obj.id = insert(cur, 'websites', fields=['hostname'],
                            args=asdict(obj))
            return obj

    def delete_by_id(self, pk):
        with in_transaction(self._conn) as cur:
            delete(cur, 'websites', args=[pk])

    def delete_by_hostname(self, hostname):
        with in_transaction(self._conn) as cur:
            delete(cur, 'websites', conditions='hostname=%s', args=[hostname])

    def list(self, pks=None, hostnames=None, order_by='id') -> List[Website]:
        conditions = '1=1'
        args = {}

        if pks is not None:
            conditions += ' and id in %(pks)s'
            args['pks'] = tuple(pks)
        if hostnames is not None:
            conditions += ' and hostname in %(hostnames)s'
            args['hostnames'] = tuple(hostnames)

        with in_transaction(self._conn) as cur:
            return select(
                cur, 'websites',
                cls=Website,
                fields=('id', 'hostname'),
                conditions=conditions,
                args=args,
                order_by=order_by
            )
