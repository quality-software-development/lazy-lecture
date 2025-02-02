import whisper
import torch

from .settings import worker_config


def init_whisper_model(worker_config) -> whisper.Whisper:
    device = (
        ("cuda" if torch.cuda.is_available() else "cpu") if worker_config.DEVICE == "auto" else worker_config.DEVICE
    )
    return whisper.load_model(
        name=worker_config.MODEL_NAME,
        device=torch.device(device),
        download_root=worker_config.DOWNLOAD_ROOT,
        in_memory=True,
    )


whisper_model = init_whisper_model(worker_config)
