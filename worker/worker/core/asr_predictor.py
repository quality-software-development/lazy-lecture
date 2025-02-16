from abc import ABC, abstractmethod
from pathlib import Path
import time
import typing as tp

from pydantic import FilePath, TypeAdapter
import whisper
import torch

from worker.core.logger import get_logger
from worker.core.settings import Settings


class ASRPredictor(ABC):
    @abstractmethod
    def transcribe_audio_file(self, path: tp.Union[str, Path], clip_timestamps: tp.Union[str, tp.List[float]]):
        pass


class WhisperASRPredictor(ASRPredictor):
    def __init__(
        self,
        whisper_model_name: str,
        download_root: str = None,
        device: tp.Literal["cpu", "cuda", "auto"] = "auto",
        preload_model: bool = True,
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.device: torch.device = self._infer_device() if device == "auto" else torch.device(device)
        self.logger.info(f"Device: {self.device}")
        time_load_started = time.time()
        self.model: whisper.Whisper = whisper.load_model(
            name=whisper_model_name,
            device=self.device,
            download_root=download_root,
            in_memory=preload_model,
        )
        self.logger.info(f"Loaded Whisper({whisper_model_name}) in {time.time() - time_load_started:.2f} seconds")

    @classmethod
    def from_settings(cls: "WhisperASRPredictor", settings: Settings, **kwargs) -> "WhisperASRPredictor":
        return cls(
            whisper_model_name=settings.whisper_model_name,
            download_root=settings.download_root,
            device=settings.device,
            **kwargs,
        )

    @staticmethod
    def _infer_device() -> torch.device:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def transcribe_audio_file(
        self, path: tp.Union[str, Path], clip_timestamps: tp.Union[str, tp.List[float]] = "0"
    ) -> tp.Tuple[str, tp.List]:
        path = Path(path)
        TypeAdapter(FilePath).validate_python(path)
        result = self.model.transcribe(str(path), clip_timestamps=clip_timestamps, language="ru")
        return result["text"], result["segments"]
