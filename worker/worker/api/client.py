import typing as tp
from urllib.parse import urljoin

from pydantic import BaseModel
import requests

from worker.core.settings import Settings
from worker.api.schemas import (
    TranscriptionChunk,
    GetTranscriptionStateRequestData,
    TranscriptionInfo,
    TranscriptionState,
    UpdateTranscriptionStateRequestData,
)
from worker.core.logger import get_logger


class APIClient:
    @classmethod
    def from_settings(cls, settings: Settings) -> "APIClient":
        return cls(str(settings.api_base_url), settings.secret_worker_token)

    def __init__(self, api_base: str, worker_token: str):
        self.api_base = api_base
        self.worker_token = worker_token
        self.logger = get_logger(self.__class__.__name__)

    def _request_to_api(
        self, request: str, request_data: tp.Union[BaseModel, None] = None, additional_params: dict = {}
    ) -> tp.Any:
        self.logger.debug(f"API request: {request=} {request_data=}")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        params = {"secret_worker_token": self.worker_token}
        if additional_params:
            params.update(additional_params)
        routes = {
            "get_transcription_info": ("get", ["worker", "transcription_status"]),
            "update_transcription_state": ("post", ["worker", "transcription_status"]),
        }
        method, route = routes[request]
        url = urljoin(self.api_base, "/".join(route))
        response = requests.request(
            method,
            url,
            params=params,
            headers=headers,
            json=request_data.model_dump(mode="json") if request_data else None,
        )
        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Bad status from api, {response.status_code=} {response.text=}")
            raise e
        return response.json()

    def get_transcription_info(self, transcription_id: int) -> tp.Union[TranscriptionInfo, None]:
        data = GetTranscriptionStateRequestData(transcription_id=transcription_id)
        response = self._request_to_api("get_transcription_info", None, data.model_dump(mode="json"))["transcription"]
        return TranscriptionInfo(**response)

    def update_transcription_state(
        self,
        transcription_id: int,
        new_state: tp.Optional[TranscriptionState] = None,
        new_chunk: tp.Optional[TranscriptionChunk] = None,
    ) -> TranscriptionInfo:
        data = UpdateTranscriptionStateRequestData(
            transcription_id=transcription_id,
            current_state=new_state,
            new_chunk=new_chunk,
        )
        response = self._request_to_api("update_transcription_state", data)["transcription"]
        return TranscriptionInfo(**response)
