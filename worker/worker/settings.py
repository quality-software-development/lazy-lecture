import os
import typing as tp
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerConfig:
    DEVICE: tp.Literal["cuda", "cpu"] = os.getenv("DEVICE", "cpu")
    MODEL_NAME: str = os.getenv("WHISPER_MODEL_NAME", "tiny")
    DOWNLOAD_ROOT: str = os.getenv("DOWNLOAD_ROOT", "/cache")


settings = WorkerConfig()
