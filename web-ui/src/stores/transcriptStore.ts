import { defineStore } from 'pinia';
import { TranscriptionsApi } from 'src/api/transcripts';
import {
    TranscriptionsMapElement,
    Transcriptions,
    ChunkedTranscription,
    TranscriptionState,
    Transcription,
} from 'src/models/transcripts';
import { date } from 'quasar';
import { ResSuccess } from 'src/models/responses';
import { useUserInfoStore } from './userInfoStore';

export const useTranscriptStore = defineStore('transcripts', {
    state: () => ({
        transcriptsMap: new Map<number, TranscriptionsMapElement>(),
        isProcessing: false,
        isCancelling: false,
        processingTranscriptionId: null as number | null,
        processingTimerId: null as NodeJS.Timeout | null,
        processsingTicks: 0,
    }),
    getters: {
        processingTranscription: (state) => {
            return state.processingTranscriptionId
                ? state.transcriptsMap.get(state.processingTranscriptionId)
                : null;
        },
    },
    actions: {
        async loadTranscriptions(page = 1, size = 100) {
            this.transcriptsMap.clear();
            const res = await TranscriptionsApi.getTranscriptions(page, size);
            if (res.successful) {
                const userInfoStore = useUserInfoStore();
                for (const transcript of (res as ResSuccess<Transcriptions>)
                    .data.transcriptions) {
                    if (transcript.creatorId === userInfoStore.userInfo?.id) {
                        this.transcriptsMap.set(transcript.id, {
                            ...transcript,
                            chunks: [],
                            markXPositions: [],
                            timeStampViews: [],
                            chunksDurationArray: [],
                        });
                    }
                }
            }
        },

        async loadTranscriptChunks(taskId: number, skip = 0, limit = 100) {
            const res = await TranscriptionsApi.getChunkedTranscription(
                taskId,
                skip,
                limit
            );
            if (res.successful) {
                const loadedChunkedTranscript = (
                    res as ResSuccess<ChunkedTranscription>
                ).data;
                if (this.transcriptsMap.has(loadedChunkedTranscript.taskId)) {
                    const transcript = this.transcriptsMap.get(
                        loadedChunkedTranscript.taskId
                    );

                    if (transcript) {
                        transcript.chunks = loadedChunkedTranscript.chunks;

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
                                (val) => val / transcript.audioLenSecs
                            ),
                        ];
                        markXPositions.pop();
                        transcript.markXPositions = markXPositions;

                        const timeStampViews = [0, ...chunksDurationArray].map(
                            (timestamp) =>
                                date.formatDate(
                                    new Date(
                                        timestamp * 1000 +
                                            new Date().getTimezoneOffset() *
                                                60000
                                    ),
                                    'HH:mm:ss'
                                )
                        );
                        timeStampViews.pop();
                        transcript.timeStampViews = timeStampViews;
                    }
                }
            }
        },

        async updateTranscriptionData(taskId: number) {
            const res = await TranscriptionsApi.getTranscriptionInfo(taskId);
            if (res.successful) {
                const transcription = this.transcriptsMap.get(taskId);
                if (transcription) {
                    this.transcriptsMap.set(taskId, {
                        ...(res as ResSuccess<Transcription>).data,
                        chunks: transcription.chunks,
                        markXPositions: transcription.markXPositions,
                        timeStampViews: transcription.timeStampViews,
                        chunksDurationArray: transcription.chunksDurationArray,
                    });
                }
            }
        },

        watchTranscriptionProcess(taskId: number) {
            this.processingTranscriptionId = taskId;
            this.isProcessing = true;
            this.processingTimerId = setInterval(async () => {
                await Promise.all([
                    this.loadTranscriptChunks(this.processingTranscriptionId!),
                    this.updateTranscriptionData(
                        this.processingTranscriptionId!
                    ),
                ]);
                this.processsingTicks++;
                const processingTranscript = this.processingTranscription;
                if (processingTranscript) {
                    if (
                        ![
                            TranscriptionState.queued,
                            TranscriptionState.in_progress,
                            TranscriptionState.processing_error,
                            TranscriptionState.cancelled,
                        ].includes(processingTranscript.currentState) ||
                        new Date().getTime() -
                            processingTranscript.updateDate.getTime() >
                            30 * 60 * 1000
                    ) {
                        this.unwatchTranscriptionProcess();
                    }
                }
            }, 2000);
        },

        unwatchTranscriptionProcess() {
            clearInterval(this.processingTimerId!);
            this.processingTimerId = null;
            this.isProcessing = false;
            this.isCancelling = false;
            this.processsingTicks = 0;
            setTimeout(() => (this.processingTranscriptionId = null));
        },

        checkProcessingTranscription() {
            if (!this.isProcessing) {
                for (const transcription of this.transcriptsMap.values()) {
                    if (
                        transcription.currentState ===
                            TranscriptionState.in_progress &&
                        new Date().getTime() -
                            transcription.updateDate.getTime() <
                            30 * 60 * 1000
                    ) {
                        this.watchTranscriptionProcess(transcription.id);
                        return transcription.id;
                    }
                }
            }
        },

        async cancelTranscriptionProcess(taskId?: number) {
            const id = taskId || this.processingTranscriptionId;
            if (id) {
                const res = await TranscriptionsApi.cancelTranscriptionProcess(
                    id
                );
                if (res.successful) {
                    if (id === this.processingTranscriptionId) {
                        this.isCancelling = true;
                    } else {
                        const transcript = this.transcriptsMap.get(id);
                        if (transcript) {
                            transcript.currentState = TranscriptionState.cancelled;
                        }
                    }
                }
            }
        },

        isTranscriptProcessing(taskId: number | undefined) {
            return (
                this.processingTranscriptionId === taskId && !this.isCancelling
            );
        },

        isTranscriptCancelling(taskId: number | undefined) {
            return (
                this.processingTranscriptionId === taskId && this.isCancelling
            );
        },
    },
});
