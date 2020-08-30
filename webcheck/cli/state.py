from typing import Union

from webcheck import database, repositories, monitoring, configuration


def lazy(fn):
    def inner(self):
        attr = f'__lazy_{fn.__name__}'
        v = getattr(self, attr, None)
        if v is None:
            v = fn(self)
            setattr(self, attr, v)
        return v

    return inner


class State:
    def __init__(self):
        self.config: Union[configuration.State, None] = None
        self.print_console = True

    @property
    @lazy
    def db_conn(self):
        return database.connect(self.config.database.url)

    @property
    @lazy
    def repo_websites(self) -> repositories.Websites:
        return repositories.Websites(self.db_conn)

    @property
    @lazy
    def repo_checks(self) -> repositories.Checks:
        return repositories.Checks(self.db_conn)

    @property
    @lazy
    def repo_results(self) -> repositories.Results:
        return repositories.Results(self.db_conn)

    @property
    @lazy
    def http_check(self) -> monitoring.HttpChecker:
        return monitoring.HttpChecker(
            timeout=self.config.http_checker.timeout,
            allow_redirects=self.config.http_checker.allow_redirects,
        )

    @property
    @lazy
    def serializer(self) -> monitoring.Pickle:
        return monitoring.Pickle()

    def producer_for(self, topic) -> monitoring.Producer:
        return monitoring.Producer(
            self.config.kafka.servers,
            topic,
            self.serializer,
            self.config.kafka.producers_options,
        )

    def consumer_for(self, topic) -> monitoring.Consumer:
        return monitoring.Consumer(
            self.config.kafka.servers,
            topic,
            self.serializer,
            self.config.kafka.consumers_options,
        )

    @property
    @lazy
    def monitoring_scheduler(self) -> monitoring.Scheduler:
        return monitoring.Scheduler(
            self.repo_websites,
            self.repo_checks,
            self.producer_for(self.config.kafka.topic_checks),
        )

    @property
    @lazy
    def monitoring_checks_worker(self) -> monitoring.ChecksWorker:
        return monitoring.ChecksWorker(
            self.http_check,
            self.consumer_for(self.config.kafka.topic_checks),
            self.producer_for(self.config.kafka.topic_results),
        )

    @property
    @lazy
    def monitoring_results_worker(self) -> monitoring.ResultsWorker:
        return monitoring.ResultsWorker(
            self.consumer_for(self.config.kafka.topic_results),
            self.repo_results,
        )
