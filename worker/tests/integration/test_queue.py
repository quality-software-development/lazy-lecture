def test_send_receive_hello_world(clean_rabbitmq_queue):
    connection, channel, queue = clean_rabbitmq_queue
    body_sent = "Hello World!"

    channel.basic_publish(exchange="", routing_key=queue, body=body_sent)

    # Consume a single message
    method_frame, header_frame, body_received = channel.basic_get(queue=queue, auto_ack=True)
    body_received = body_received.decode("utf-8")
    assert method_frame is not None
    assert body_received == body_sent, f"{body_received=} != {body_sent=}"
