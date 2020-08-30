import logging
from typing import Dict

from webcheck.repositories import Checks, Check, Websites, Website
from webcheck.time import now
from .kafka import Producer
from .models import Task

logger = logging.getLogger(__name__)


def build_url(hostname, protocol):
    return f'{protocol}://{hostname}'


def inc_run_after(check):
    check.run_after = max(
        check.run_after + check.interval,
        now() + check.interval,
    )


class Scheduler:
    def __init__(
        self,
        websites: Websites,
        checks: Checks,
        producer: Producer,
    ):
        self.__websites = websites
        self.__checks = checks
        self.__producer = producer

    def _websites_by_id(self, pks):
        r = {}
        for obj in self.__websites.list(pks=pks or None):
            r[obj.id] = obj
        return r

    def schedule(self):
        n = now()
        checks = self.__checks.list(run_after__le=n)
        websites_by_id = self._websites_by_id([x.website_id for x in checks])

        logger.info("scheduling %d checks running after %s",
                    len(checks), n.isoformat())

        for check in checks:
            task = self._to_task(check, websites_by_id)
            if not task:
                continue

            self.__producer.send(task)

            # reschedule
            inc_run_after(check)
            self.__checks.update(check)
            logger.info("scheduled %s, next run %s", task, check.run_after)

        self.__producer.flush()
        logger.info("scheduling complete")

    @staticmethod
    def _to_task(check: Check, website_ids: Dict[int, Website]):
        website = website_ids.get(check.website_id)
        if not website:
            logger.warning('missing website for a check_id=%s', check.id)
            return None

        # todo: check both http and https
        url = build_url(website.hostname, 'https')

        return Task(
            check_id=check.id,
            url=url,
            expect_http_code=check.expect_http_code,
            expect_body_pattern=check.expect_body_pattern,
        )
