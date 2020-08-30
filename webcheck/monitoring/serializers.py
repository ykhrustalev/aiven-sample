import abc
import pickle


class Serializer(abc.ABC):
    def encode(self, obj):
        pass

    def decode(self, data):
        pass


class Pickle(Serializer):
    def encode(self, obj):
        return pickle.dumps(obj)

    def decode(self, data):
        return pickle.loads(data)
