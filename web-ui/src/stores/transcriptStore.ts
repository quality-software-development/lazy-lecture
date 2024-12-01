import { defineStore } from 'pinia';
import { getTranscripts, getTranscriptChunked } from 'src/api/transcripts';
import {
    IChunk,
    ITranscriptsMapElement,
    TranscriptStatus,
} from 'src/models/transcripts';
import { date } from 'quasar';

export const useTranscriptStore = defineStore('transcripts', {
    state: () => ({
        transcriptsMap: new Map<number, ITranscriptsMapElement>(),
    }),
    actions: {
        async loadTranscripts(skip: number, limit: number) {
            const transcripts = await getTranscripts(skip, limit);
            if (!transcripts) {
                throw new Error('Не удалось загрузить транскрипции');
            }
            for (const transcript of transcripts) {
                this.transcriptsMap.set(transcript.taskId, {
                    ...transcript,
                    chunks: [],
                    markXPositions: [],
                    timeStampViews: [],
                    chunksDurationArray: [],
                });
            }
        },
        async loadTranscriptChunks(
            taskId: number,
            skip: number,
            limit: number
        ) {
            const loadedTranscriptChunked = await getTranscriptChunked(
                taskId,
                skip,
                limit
            );
            if (this.transcriptsMap.has(loadedTranscriptChunked.taskId)) {
                const transcript = this.transcriptsMap.get(
                    loadedTranscriptChunked.taskId
                );

                if (transcript) {
                    transcript.chunks = loadedTranscriptChunked.chunks;

                    const chunksDurationArray = transcript.chunks.reduce(
                        (a, b, idx) => {
                            if (idx == 0) {
                                a.push(b.duration);
                            } else {
                                a.push(a[idx - 1] + b.duration);
                            }
                            return a;
                        },
                        [] as number[]
                    );
                    transcript.chunksDurationArray = chunksDurationArray;

                    const markXPositions = [
                        0,
                        ...chunksDurationArray.map(
                            (val) => val / transcript.duration
                        ),
                    ];
                    markXPositions.pop();
                    transcript.markXPositions = markXPositions;

                    const timeStampViews = [0, ...chunksDurationArray].map(
                        (timestamp) =>
                            date.formatDate(
                                new Date(
                                    timestamp * 1000 +
                                        new Date().getTimezoneOffset() * 60000
                                ),
                                'HH:mm:ss'
                            )
                    );
                    timeStampViews.pop();
                    transcript.timeStampViews = timeStampViews;
                }
            }
        },
    },
});
