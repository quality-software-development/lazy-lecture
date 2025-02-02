from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "FastAPI JWT Auth API"
    VERSION: str = "1.0.0"

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "Shkibidi_to1let!"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SECRET_KEY: str = "s3cr3t_k3y"
    ALGORITHM: str = "HS256"

    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "database"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_URI: str | None = None

    OBJECT_STORAGE_PATH: str = "object_storage"

    PIKA_HOST: str = "localhost"
    PIKA_PORT: int = 5672
    PIKA_USER: str = "rmuser"
    PIKA_PASS: str = "rmpassword"
    PIKA_QUEUE: str = "task_queue"

    DEFAULT_CHUNK_SIZE: float = 60 * 15

    SECRET_WORKER_TOKEN: str = "71y209716yc20n971yoj"
    SECRET_ADMIN_TOKEN: str = "verysecretadmintokenyeah"

    @model_validator(mode="after")
    def validator(cls, values: "Settings") -> "Settings":
        values.POSTGRES_URI = (
            f"{values.POSTGRES_USER}:{values.POSTGRES_PASSWORD}@"
            f"{values.POSTGRES_HOST}:{values.POSTGRES_PORT}/{values.POSTGRES_DB}"
        )
        return values


def get_settings():
    return Settings()


settings = get_settings()
