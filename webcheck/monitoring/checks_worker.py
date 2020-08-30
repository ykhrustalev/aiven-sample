import logging

from .checkers import Checker
from .kafka import Consumer, Producer

logger = logging.getLogger(__name__)


class ChecksWorker:
    def __init__(
        self,
        checker: Checker,
        consumer: Consumer,
        producer: Producer,
    ):
        self.__checker = checker
        self.__consumer = consumer
        self.__producer = producer

    def execute(self):
        for task in self.__consumer.receive():
            try:
                res = self.__checker.check(task)
                self.__producer.send(res)
                self.__producer.flush()
                logger.info("handled %s with %s", task, res)
            except Exception:
                logger.exception("failed to handle %s", task)
