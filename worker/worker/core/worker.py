import json
from pathlib import Path
import time
import traceback
from typing import Generator, List, Union

from aio_pika import IncomingMessage
import requests

from worker.api.client import APIClient
from worker.core.asr_predictor import WhisperASRPredictor, ASRPredictor
from worker.core.settings import Settings
from worker.core.task_consumer import AioPikaTaskConsumer
from worker.api.schemas import TaskData, TranscriptionChunk, TranscriptionInfo, TranscriptionState
from worker.core.object_storage import ObjectStorage, SimpleObjectStorage
from worker.core.logger import get_logger


class LazyLectureWorker:
    TERMINAL_STATES = [
        TranscriptionState.COMPLETED,
        TranscriptionState.COMPLETED_PARTIALLY,
        TranscriptionState.PROCESSING_FAIL,
        TranscriptionState.CANCELLED,
    ]

    def __init__(self, settings: Settings):
        # Composite pattern
        self.task_consumer: AioPikaTaskConsumer = AioPikaTaskConsumer.from_settings(settings)
        self.api_client: APIClient = APIClient.from_settings(settings)
        self.object_storage: ObjectStorage = SimpleObjectStorage.from_settings(settings)
        self.asr_predictor: ASRPredictor = WhisperASRPredictor.from_settings(settings)

        # Logger
        self.logger = get_logger(self.__class__.__name__)

        self.logger.info("Worker initialized successfully")

    async def _nack_for_state(self, message, transcription_info: TranscriptionInfo, task_data: TaskData) -> bool:
        if transcription_info.current_state in self.TERMINAL_STATES:
            self.logger.info("Task nacked due to being in terminal state already")
            await message.nack(requeue=False)
        elif (
            transcription_info.current_state == TranscriptionState.PROCESSING_ERROR
            and transcription_info.error_count >= 3
        ):
            self.api_client.update_transcription_state(task_data.transcription_id, TranscriptionState.PROCESSING_FAIL)
            self.logger.info("Task nacked due to error_count >= 3, changed state to processing fail")
            await message.nack(requeue=False)
        elif transcription_info.current_state == TranscriptionState.IN_PROGRESS:
            self.api_client.update_transcription_state(task_data.transcription_id, TranscriptionState.PROCESSING_FAIL)
            self.logger.info(
                "Task nacked due to being in progress. Changing status to processing fail due to the fact that if the processing is still going it will change it to in progress again"
            )
            await message.nack(requeue=False)
        else:
            return False
        return True

    def _get_audio_by_user_id(self, user_id):
        user_audio = self.object_storage.get_user_audio(user_id)
        if user_audio is None:
            raise FileNotFoundError(f"User audio is not found in object storage {task_data.user_id=}")
        self.logger.info(f"Found user audio at {str(user_audio)}")
        return user_audio

    def _infer_audio(self, user_audio, audio_len_secs: float, chunk_size_secs: int) -> Generator:
        self.logger.info("Inference Begin!")
        self.logger.info(f"Audio length is {audio_len_secs:.2f} seconds")
        clip_timestamps = [
            [v, min(audio_len_secs, v + chunk_size_secs)] for v in range(0, int(audio_len_secs) + 1, chunk_size_secs)
        ]
        clip_timestamps[-1] = [
            clip_timestamps[-1][0],
        ]
        # TODO: return max chunk_no to TranscriptionInfo to skip them
        for chunk_no, clip_timestamp in enumerate(clip_timestamps):
            text = self._infer_chunk(user_audio, clip_timestamp, audio_len_secs)
            yield TranscriptionChunk(text=text, chunk_no=chunk_no)

    async def process_message(self, message: IncomingMessage):
        decoded_message = message.body.decode()
        task_data = TaskData(**json.loads(decoded_message))
        try:
            transcription_info: TranscriptionInfo = self.api_client.get_transcription_info(task_data.transcription_id)
            self.logger.info(f"Received a task: {task_data.model_dump_json()}")
            self.logger.info(f"Transcription Info: {transcription_info.model_dump_json()}")

            nacked = self._nack_for_state(message, transcription_info)
            if nacked:
                return
            if transcription_info.current_state == TranscriptionState.QUEUED:
                self.api_client.update_transcription_state(task_data.transcription_id, TranscriptionState.IN_PROGRESS)

            # Process audio
            user_audio = self._get_audio_by_user_id(task_data.user_id)
            for text_chunk in self._infer_audio(
                user_audio, transcription_info.audio_len_secs, transcription_info.chunk_size_secs
            ):
                transcription_info = self.api_client.get_transcription_info(task_data.transcription_id)
                if transcription_info.current_state in [
                    TranscriptionState.CANCELLED,
                    TranscriptionState.COMPLETED_PARTIALLY,
                ]:
                    self.api_client.update_transcription_state(
                        task_data.transcription_id, TranscriptionState.COMPLETED_PARTIALLY, new_chunk=text_chunk
                    )
                    self.logger.info("Task was cancelled, nacking")
                    await message.nack(requeue=False)
                    return
            new_state = TranscriptionState.COMPLETED
            self.api_client.update_transcription_state(task_data.transcription_id, new_state=new_state)
            self.logger.info("Inference complete!")
            await message.ack()
            self.object_storage.remove_user_audio(task_data.user_id)
        except requests.exceptions.HTTPError as e:
            self.logger.warning(f"HTTP Error occured: {e}. Traceback: {traceback.format_exc()}")
            await message.nack(requeue=False)
        except requests.exceptions.ConnectionError as e:
            self.logger.error(
                f"Exception {e} occured, API is probably unavailable. Traceback: {traceback.format_exc()}"
            )
            await message.nack(requeue=True)
            self.logger.error("Returned message to queue")
        except Exception as e:
            self.logger.warning(
                f"Exception {e} occured during processing message. Check traceback below.\n{traceback.format_exc()}"
            )
            self.logger.warning("Incrementing error count for the task")
            error_count = self.api_client.get_transcription_info(task_data.transcription_id).error_count
            if error_count < 3:
                self.api_client.update_transcription_state(
                    task_data.transcription_id, TranscriptionState.PROCESSING_ERROR
                )
                await message.nack(requeue=True)
            else:
                self.api_client.update_transcription_state(
                    task_data.transcription_id, TranscriptionState.PROCESSING_FAIL
                )
                await message.nack(requeue=False)

    def _infer_chunk(self, user_audio: Path, clip_timestamp: Union[str, List[float]], audio_len_secs: int) -> str:
        chunk_start = time.time()
        text = self.asr_predictor.transcribe_audio_file(user_audio, clip_timestamp)
        chunk_time = time.time() - chunk_start
        clip_end = clip_timestamp[1] if len(clip_timestamp) == 2 else audio_len_secs
        clip_length = clip_end - clip_timestamp[0]
        speedup = clip_length / chunk_time
        self.logger.info(
            f"Clip {clip_timestamp} inferred in {chunk_time:.2f}s (x{speedup:.1f} speedup) Text sample: {text[:250]}"
        )
        return text

    async def start(self):
        self.logger.info("Begun processing messages")
        async for message in self.task_consumer.process_messages():
            await self.process_message(message)
