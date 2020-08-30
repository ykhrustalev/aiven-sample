import logging

from webcheck.repositories import Results
from .kafka import Consumer

logger = logging.getLogger(__name__)


class ResultsWorker:
    def __init__(self, consumer: Consumer, results: Results):
        self.__consumer = consumer
        self.__results = results

    def execute(self):
        for res in self.__consumer.receive():
            try:
                self.__results.create(res)
                logger.info("saved %s", res)
            except Exception:
                logger.exception("failed to handle %s", res)
