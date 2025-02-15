from pathlib import Path
import typing as tp

from pydantic import FilePath, TypeAdapter
import whisper
import torch


class WhisperPredictor:
    def __init__(
        self,
        whisper_model_name: str,
        download_root: str = None,
        device: tp.Literal["cpu", "cuda", "auto"] = "auto",
        preload_model: bool = False,
    ):
        self.device: torch.device = self._infer_device() if device == "auto" else torch.device(device)
        self.model: whisper.Whisper = whisper.load_model(
            name=whisper_model_name,
            device=self.device,
            download_root=download_root,
            in_memory=preload_model,
        )

    @staticmethod
    def _infer_device() -> torch.device:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def transcribe_audio_file(
        self, path: tp.Union[str, Path], clip_timestamp: tp.Optional[tp.Tuple[float, float]] = "0"
    ) -> tp.Tuple[str, tp.List]:
        path = Path(path)
        TypeAdapter(FilePath).validate_python(path)
        result = self.model.transcribe(str(path), clip_timestamps=clip_timestamp, language="ru")
        return result["text"], result["segments"]
