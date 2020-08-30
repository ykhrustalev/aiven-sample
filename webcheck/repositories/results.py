from dataclasses import asdict
from typing import List

from webcheck.database import in_transaction
from webcheck.validation import validate
from .errors import DoesNotExistError
from .models import Repo, Result
from .queries import insert, delete, select, exists

scheme_create = dict(
    check_id=dict(type='integer'),
    succeed=dict(type='boolean'),
    started_at=dict(type='datetime'),
    duration=dict(type='timedelta', minseconds=0),
    http_code=dict(type='integer'),
    message=dict(type='string', empty=True),
)


class Results(Repo):
    def create(self, obj: Result) -> Result:
        validate(scheme_create, obj)

        with in_transaction(self._conn) as cur:
            if not exists(cur, 'checks', 'id=%s', args=[obj.check_id]):
                raise DoesNotExistError("corresponding check doesn't exist")

            insert(cur, 'results', args=asdict(obj), fields=(
                'check_id',
                'succeed',
                'started_at',
                'duration',
                'http_code',
                'message',
            ), returning='returning 1')
            return obj

    def delete_for_check_id(self, check_id):
        with in_transaction(self._conn) as cur:
            delete(cur, 'results', conditions='check_id=%s', args=[check_id])

    def list(self, check_ids=None, started_at__le=None, started_at__ge=None,
             order_by='started_at') -> List[Result]:
        conditions = '1=1'
        args = {}

        if check_ids is not None:
            conditions += ' and check_id in %(check_ids)s'
            args['check_ids'] = tuple(check_ids)
        if started_at__le is not None:
            conditions += ' and started_at <= %(started_at__le)s'
            args['started_at__le'] = started_at__le
        if started_at__ge is not None:
            conditions += ' and started_at >= %(started_at__ge)s'
            args['started_at__ge'] = started_at__ge

        with in_transaction(self._conn) as cur:
            return select(
                cur, 'results',
                cls=Result,
                fields=(
                    'check_id',
                    'succeed',
                    'started_at',
                    'duration',
                    'http_code',
                    'message',
                ),
                conditions=conditions,
                args=args,
                order_by=order_by,
            )
