import pika


def test_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            port=5672,
            credentials=pika.PlainCredentials(username="user", password="pass"),
            connection_attempts=3,
            retry_delay=5,
        )
    )
    channel = connection.channel()
    queue_name = "task_queue"
    channel.queue_declare(queue=queue_name, durable=True)
    print("Connection successful")
    connection.close()


test_connection()
