from abc import ABC, abstractmethod
import typing as tp

import aio_pika

from worker.core.settings import Settings
from worker.core.logger import get_logger


class TaskConsumer(ABC):
    @abstractmethod
    def process_messages() -> tp.Iterable:
        pass


class AioPikaTaskConsumer(TaskConsumer):
    @classmethod
    def from_settings(cls, settings: Settings) -> "AioPikaTaskConsumer":
        return cls(settings.aio_pika_connection_string, settings.pika_queue)

    def __init__(self, aio_pika_connection_string: str, queue_name: str):
        super().__init__()
        self.connection = None
        self.connection_string = aio_pika_connection_string
        self.queue_name = queue_name
        self.logger = get_logger(self.__class__.__name__)

    async def _connect(self):
        if self.connection is None:
            self.connection = await aio_pika.connect_robust(self.connection_string)
            self.logger.info("Connected to RMQ successfully")

    async def _read_messages(self) -> tp.AsyncGenerator[aio_pika.IncomingMessage, None]:
        async with self.connection as connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(self.queue_name, durable=True)
            iterator = queue.iterator()
            async with iterator as queue_iter:
                async for message in queue_iter:
                    async with message.process(ignore_processed=True):
                        yield message

    async def process_messages(self) -> tp.AsyncGenerator[aio_pika.IncomingMessage, None]:
        await self._connect()
        async for message in self._read_messages():
            yield message
