import click

from .settings import worker_config
from .task_queue import send_transcription_job_to_queue, get_pika_connection


@click.command()
@click.argument("transcription_id", type=click.IntRange(0))
@click.argument("author_id", type=click.IntRange(0))
@click.option("--host", type=str, default=None)
@click.option("--port", type=int, default=None)
def cli_send_job_to_queue(transcription_id: int, author_id: int, host, port):
    connection, channel = get_pika_connection(host, port)
    send_transcription_job_to_queue(channel, worker_config.PIKA_QUEUE, transcription_id, author_id)
    connection.close()


if __name__ == "__main__":
    cli_send_job_to_queue()
