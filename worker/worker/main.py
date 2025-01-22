import random
import time
import pika

from .settings import worker_config, WorkerConfig
from .worker_callback import process_transcription_job_messages


class QueueWorker:
    def __init__(self, worker_config: WorkerConfig):
        self.worker_config = worker_config

    def start(self):
        worker_config = self.worker_config
        while True:
            try:
                print("[*] Connecting to RMQ...")
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=worker_config.PIKA_HOST,
                        port=worker_config.PIKA_PORT,
                        credentials=pika.PlainCredentials(
                            username=worker_config.PIKA_USER, password=worker_config.PIKA_PASS
                        ),
                        connection_attempts=3,
                        retry_delay=5,
                    )
                )
                print("[*] Connected to RMQ!")
                channel = connection.channel()

                channel.queue_declare(queue=worker_config.PIKA_QUEUE, durable=True)
                print("[*] Waiting for messages. To exit press CTRL+C")

                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=worker_config.PIKA_QUEUE,
                    on_message_callback=lambda ch, method, properties, body: process_transcription_job_messages(
                        ch, method, body
                    ),
                )
                channel.start_consuming()
            except:
                time.sleep(random.randint(0, 10))


if __name__ == "__main__":
    worker = QueueWorker(worker_config)
    worker.start()
