import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from pydantic import DirectoryPath, TypeAdapter

from worker.core.settings import Settings
from worker.core.logger import get_logger


class ObjectStorage(ABC):
    @abstractmethod
    def get_user_audio(self, user_id: int) -> Path:
        pass

    @abstractmethod
    def remove_user_audio(self, user_id: int) -> None:
        pass


class SimpleObjectStorage(ObjectStorage):
    @classmethod
    def from_settings(cls, settings: Settings) -> "ObjectStorage":
        return cls(settings.object_storage_path)

    def __init__(self, storage_root: Union[Path, str]):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.storage_root = TypeAdapter(DirectoryPath).validate_python(Path(storage_root))

    def _get_audio_path_by_user_id(self, user_id: int) -> Union[Path, None]:
        audio_path: Path = self.storage_root / f"{user_id}.mp3"
        if not audio_path.exists() or not audio_path.is_file():
            return None
        return audio_path

    def get_user_audio(self, user_id: int) -> Union[Path, None]:
        return self._get_audio_path_by_user_id(user_id)

    def remove_user_audio(self, user_id: int) -> None:
        user_audio_path = self._get_audio_path_by_user_id(user_id)
        if user_audio_path is not None and user_audio_path.exists():
            os.unlink(user_audio_path)
