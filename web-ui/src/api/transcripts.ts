import { api } from 'src/boot/axios';
import {
    TranscriptGeneralDTO,
    ITranscriptGeneral,
    TranscriptChunkedDTO,
    ITranscriptChunked,
} from 'src/models/transcripts';

export async function getTranscripts(
    skip = 0,
    limit = 100
): Promise<ITranscriptGeneral[]> {
    // const accessToken = localStorage.getItem('accessToken');
    // if (!accessToken) {
    //     throw new Error('Вы не авторизованы.');
    // }
    // const res = await api.get<TranscriptDTO[]>(`/transcriptions?skip=${skip}&limit=${limit}`, {
    //     headers: {
    //         Authorization: `Bearer ${accessToken}`,
    //     },
    // });
    // if (res.status === 200) {
    //     return res.data.map((transcript) => {
    //         return {
    //             taskId: transcript.task_id,
    //             text: transcript.transcription,
    //             timeStamp: new Date(transcript.timestamp),
    //             duration: transcript.transcript_length_secs,
    //             status: transcript.status,
    //         }
    //     });
    // } else {
    //     throw new Error('Не удалось загрузить транскрипции.');
    // }
    return [
        {
            taskId: 12345,
            text: 'This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio.',
            timeStamp: new Date('2024-10-22T12:34:56Z'),
            duration: 2500,
            status: 3,
        },
        {
            taskId: 67890,
            text: 'This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio.',
            timeStamp: new Date('2024-10-22T12:34:56Z'),
            duration: 1550,
            status: 1,
        },
    ];
}

export async function getTranscriptChunked(
    taskId: number,
    skip: number,
    limit: number
): Promise<ITranscriptChunked> {
    // const accessToken = localStorage.getItem('accessToken');
    // if (!accessToken) {
    //     throw new Error('Вы не авторизованы.');
    // }
    // const res = await api.get<TranscriptChunkedDTO>(
    //     `/transcript?task_id=${taskId}&skip=${skip}&limit=${limit}`,
    //     {
    //         headers: {
    //             Authorization: `Bearer ${accessToken}`,
    //         },
    //     }
    // );
    // if (res.status === 200) {
    //     return {
    //         taskId: res.data.task_id,
    //         chunks: res.data.transcription_chunks.map((chunk) => {
    //             return {
    //                 index: chunk.chunk_order,
    //                 duration: chunk.chunk_size_secs,
    //                 text: chunk.transcription,
    //             };
    //         }),
    //     };
    // } else {
    //     throw new Error(`Не удалось загрузить транскрипцию с id = ${taskId}.`);
    // }
    const chunks = [
        {
            index: 1,
            duration: 600,
            text: 'This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription. This is the first part of the transcription.',
        },
        {
            index: 2,
            duration: 350,
            text: 'This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription.This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription. This is the second part of the transcription.',
        },
        {
            index: 3,
            duration: 600,
            text: 'This is the third part of the transcription. This is the third part of the transcription. This is the third part of the transcription. This is the third part of the transcription. This is the third part of the transcription. This is the third part of the transcription. This is the third part of the transcription.',
        },
    ];
    if (taskId === 12345) {
        chunks.push({
            index: 4,
            duration: 600,
            text: 'This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription. This is the fourth part of the transcription.',
        });
    }

    return {
        taskId,
        chunks,
    };
}
