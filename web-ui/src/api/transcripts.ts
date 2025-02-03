import { ResSuccess, ResError } from 'src/models/responses';
import {
    ChunkedTranscription,
    TranscriptionsQueryDTO,
    Transcriptions,
    TranscriptionState,
    TranscriptionQueryDTO,
    TranscriptionInfoQueryDTO,
    Transcription,
} from 'src/models/transcripts';
import { BaseApi } from './baseApi';

export class TranscriptionsApi extends BaseApi {
    private static getTranscriptionFromDTO(
        DTO: TranscriptionInfoQueryDTO
    ): Transcription {
        return {
            id: DTO.id,
            creatorId: DTO.creator_id,
            audioLenSecs: DTO.audio_len_secs,
            chunkSizeSecs: DTO.chunk_size_secs,
            currentState: TranscriptionState[DTO.current_state],
            createDate: new Date(`${DTO.create_date}Z`),
            updateDate: new Date(`${DTO.update_date}Z`),
            description: DTO.description,
        };
    }

    static async getTranscriptions(
        page = 1,
        size = 50
    ): Promise<ResSuccess<Transcriptions> | ResError> {
        return this.runRequest<Transcriptions, TranscriptionsQueryDTO>(
            'get',
            `/transcriptions?page=${page}&size=${size}`,
            (res) => {
                return {
                    page: res.data.page,
                    pages: res.data.pages,
                    size: res.data.size,
                    total: res.data.total,
                    transcriptions: res.data.transcriptions.map(
                        (transcription) =>
                            this.getTranscriptionFromDTO(transcription)
                    ),
                };
            },
            'Не удалось загрузить транскрипции.'
        );
    }

    static async getChunkedTranscription(
        taskId: number,
        skip: number,
        limit: number
    ): Promise<ResSuccess<ChunkedTranscription> | ResError> {
        return this.runRequest<ChunkedTranscription, TranscriptionQueryDTO>(
            'get',
            `/transcript?task_id=${taskId}&skip=${skip}&limit=${limit}`,
            (res) => {
                return {
                    taskId,
                    chunks: res.data.transcriptions.map((chunk) => {
                        return {
                            index: chunk.chunk_order,
                            duration: chunk.chunk_size_secs,
                            text: chunk.transcription,
                        };
                    }),
                };
            },
            `Не удалось загрузить части транскрипции с id = ${taskId}.`
        );
    }

    static async getTranscriptionInfo(
        taskId: number
    ): Promise<ResSuccess<Transcription> | ResError> {
        return this.runRequest<Transcription, TranscriptionInfoQueryDTO>(
            'get',
            `/transcript/info?transcript_id=${taskId}`,
            (res) => this.getTranscriptionFromDTO(res.data),
            `Не удалось загрузить транскрипцию с id = ${taskId}.`
        );
    }

    static async cancelTranscriptionProcess(
        taskId: number
    ): Promise<ResSuccess<null> | ResError> {
        return this.runRequest<null, any>(
            'post',
            `/transcript/cancel?transcript_id=${taskId}`,
            () => null,
            `Не удалось отменить обработку транскрипции с id = ${taskId}.`,
        );
    }
}
