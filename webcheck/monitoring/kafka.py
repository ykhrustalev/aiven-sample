from typing import List

from kafka import KafkaProducer, KafkaConsumer

from .serializers import Serializer


class Producer:
    def __init__(self,
                 servers: List[str],
                 topic: str,
                 serializer: Serializer,
                 extra_options):
        self.__topic = topic
        self.__servers = servers
        self.__serializer = serializer
        self.__extra_options = extra_options

    @property
    def __producer(self):
        return KafkaProducer(
            bootstrap_servers=self.__servers,
            **self.__extra_options,
        )

    def send(self, obj):
        data = self.__serializer.encode(obj)
        self.__producer.send(self.__topic, data)

    def flush(self):
        self.__producer.flush()


class Consumer:
    def __init__(
        self,
        servers: List[str],
        topic: str,
        serializer: Serializer,
        extra_options
    ):
        self.__topic = topic
        self.__servers = servers
        self.__serializer = serializer
        self.__extra_options = extra_options

    @property
    def __consumer(self):
        return KafkaConsumer(
            self.__topic,
            bootstrap_servers=self.__servers,
            group_id=f'{self.__topic}-worker',
            **self.__extra_options,
        )

    def receive(self):
        for msg in self.__consumer:
            yield self.__serializer.decode(msg.value)
