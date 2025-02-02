import whisper
import torch

from .settings import worker_config


def init_whisper_model(worker_config) -> whisper.Whisper:
    device = worker_config.DEVICE
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return whisper.load_model(
        name=worker_config.MODEL_NAME,
        device=device,
        download_root=worker_config.DOWNLOAD_ROOT,
        in_memory=True,
    )


whisper_model = init_whisper_model(worker_config)
