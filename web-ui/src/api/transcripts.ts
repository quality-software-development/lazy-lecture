import { api } from 'src/boot/axios';
import { TranscriptDTO } from 'src/models/transcripts';

export async function getTranscripts(skip = 0, limit = 100) {
    // const accessToken = localStorage.getItem('accessToken');
    // if (!accessToken) {
    //     throw new Error('Вы не авторизованы.');
    // }
    // const res = await api.get<TranscriptDTO[]>(`/transcriptions?skip=${skip}&limit=${limit}`, {
    //     headers: {
    //         Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
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
            duration: 60 * 120,
            status: 3,
        },
        {
            taskId: 12345,
            text: 'This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio. This is the transcribed text of the audio.',
            timeStamp: new Date('2024-10-22T12:34:56Z'),
            duration: 60 * 120,
            status: 1,
        },
    ];
}
