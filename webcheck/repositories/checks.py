from dataclasses import asdict
from typing import List

from webcheck.database import in_transaction
from webcheck.time import now
from webcheck.validation import validate
from .errors import DoesNotExistError
from .models import Repo, Check
from .queries import insert, delete, select, exists, update

scheme_create = dict(
    id=dict(type='integer', nullable=True),
    website_id=dict(type='integer'),
    interval=dict(type='timedelta', minseconds=30),
    run_after=dict(type='datetime', nullable=True),
    expect_http_code=dict(type='integer'),
    expect_body_pattern=dict(type='string', empty=True),
)

scheme_update = scheme_create.copy()
scheme_update['id'] = dict(type='integer')
scheme_update['run_after'] = dict(type='datetime')


class Checks(Repo):
    def create(self, obj: Check) -> Check:
        validate(scheme_create, obj)

        with in_transaction(self._conn) as cur:
            if not exists(cur, 'websites', 'id=%s', args=[obj.website_id]):
                raise DoesNotExistError("corresponding website doesn't exist")

            if obj.run_after is None:
                obj.run_after = now() + obj.interval

            obj.id = insert(cur, 'checks', args=asdict(obj), fields=(
                'website_id',
                'interval',
                'run_after',
                'expect_http_code',
                'expect_body_pattern',
            ))
            return obj

    def update(self, obj: Check) -> Check:
        validate(scheme_update, obj)

        with in_transaction(self._conn) as cur:
            update(
                cur, 'checks',
                conditions='id = %(id)s',
                fields=(
                    'website_id',
                    'interval',
                    'run_after',
                    'expect_http_code',
                    'expect_body_pattern',
                ),
                args=asdict(obj),
            )
            return obj

    def delete_by_id(self, pk):
        with in_transaction(self._conn) as cur:
            delete(cur, 'checks', args=[pk])

    def delete_for_website_id(self, website_id):
        with in_transaction(self._conn) as cur:
            delete(cur, 'checks', conditions='website_id=%s',
                   args=[website_id])

    def list(self, pks=None, website_ids=None, run_after__le=None,
             order_by='id') -> List[Check]:
        conditions = '1=1'
        args = {}

        if pks is not None:
            conditions += ' and id in %(pks)s'
            args['pks'] = tuple(pks)
        if website_ids is not None:
            conditions += ' and website_id in %(website_ids)s'
            args['website_ids'] = tuple(website_ids)
        if run_after__le is not None:
            conditions += ' and run_after <= %(run_after__le)s'
            args['run_after__le'] = run_after__le

        with in_transaction(self._conn) as cur:
            return select(
                cur, 'checks',
                cls=Check,
                fields=(
                    'id',
                    'website_id',
                    'interval',
                    'run_after',
                    'expect_http_code',
                    'expect_body_pattern',
                ),
                conditions=conditions,
                args=args,
                order_by=order_by,
            )
