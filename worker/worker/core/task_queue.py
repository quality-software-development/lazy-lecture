from abc import ABC, abstractmethod

import pika


class TaskQueueManager(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def start_consuming(self) -> None:
        pass


class PikaTaskQueueManager(TaskQueueManager):
    def __init__(self, connection_params: pika.ConnectionParameters):
        super().__init__()
        self.connection_params = connection_params
