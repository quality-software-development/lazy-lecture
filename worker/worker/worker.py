import requests
import pika

from .settings import worker_config, WorkerConfig


def callback(ch, method, properties, body):
    try:
        message = body.decode()
        print("[x] Received message: ", str(message))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[x] Done")
    except Exception as e:
        print(f"[x] Error! {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker(worker_config: WorkerConfig):
    print("[*] Connecting to RMQ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=worker_config.PIKA_HOST,
            port=worker_config.PIKA_PORT,
            credentials=pika.PlainCredentials(username=worker_config.PIKA_USER, password=worker_config.PIKA_PASS),
            connection_attempts=3,
            retry_delay=5,
        )
    )
    print("[*] Connected to RMQ!")
    channel = connection.channel()

    channel.queue_declare(queue=worker_config.PIKA_QUEUE, durable=True)
    print("[*] Waiting for messages. To exit press CTRL+C")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=worker_config.PIKA_QUEUE, on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    start_worker(worker_config)
