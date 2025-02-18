import typing as tp

import whisper
from pydantic import AnyHttpUrl, DirectoryPath, PositiveInt, field_validator
from pydantic_settings import BaseSettings

WHISPER_MODEL_NAMES = (
    "tiny.en",
    "tiny",
    "base.en",
    "base",
    "small.en",
    "small",
    "medium.en",
    "medium",
    "large-v1",
    "large-v2",
    "large-v3",
    "large",
    "large-v3-turbo",
    "turbo",
)


class Settings(BaseSettings):
    # Object storage
    object_storage_path: DirectoryPath = "/object_storage"

    # Inference
    device: tp.Literal["cuda", "cpu", "auto"] = "auto"
    whisper_model_name: str = "tiny"
    download_root: str = "/cache"

    # Queue connection
    pika_host: str = "rabbitmq"
    pika_port: PositiveInt = 5672
    pika_user: str = "rmuser"
    pika_pass: str = "rmpassword"
    pika_queue: str = "task_queue"

    # Api communication
    secret_worker_token: str = "<secret_worker_token_is_not_specified>"
    api_base_url: AnyHttpUrl = "http://api:8000"

    @field_validator("whisper_model_name")
    def validate_option(cls, v):
        assert v in whisper.available_models()
        return v

    @property
    def aio_pika_connection_string(self) -> str:
        return f"amqp://{self.pika_user}:{self.pika_pass}@{self.pika_host}:{self.pika_port}/"
