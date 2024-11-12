import whisper

from .settings import worker_config


def init_whisper_model(worker_config) -> whisper.Whisper:
    return whisper.load_model(
        name=worker_config.MODEL_NAME,
        device=worker_config.DEVICE,
        download_root=worker_config.DOWNLOAD_ROOT,
        in_memory=True,
    )


whisper_model = init_whisper_model(worker_config)
