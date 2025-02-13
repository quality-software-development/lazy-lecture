import whisper
import torch

from worker.core.settings import settings, Settings


def init_whisper_model(settings: Settings) -> whisper.Whisper:
    device = ("cuda" if torch.cuda.is_available() else "cpu") if settings.device == "auto" else settings.device
    return whisper.load_model(
        name=settings.whisper_model_name,
        device=torch.device(device),
        download_root=settings.download_root,
        in_memory=True,
    )


whisper_model = init_whisper_model(settings)
