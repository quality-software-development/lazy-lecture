import { defineStore } from 'pinia';
import { TranscriptionsApi } from 'src/api/transcripts';
import {
    TranscriptionsMapElement,
    Transcriptions,
    ChunkedTranscription,
    TranscriptionState,
    Transcription,
} from 'src/models/transcripts';
import { formatTimestamp } from 'src/composables/formatTimestamp';
import { ResSuccess } from 'src/models/responses';
import { useUserInfoStore } from './userInfoStore';
import { Notify } from 'quasar';

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
            console.log('[TranscriptStore] loadTranscriptions() called');
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
                        console.log('[TranscriptStore] added to transcriptsMap:', transcript);
                    }
                }
            }
        },

        async loadTranscriptChunks(taskId: number, skip = 0, limit = 100) {
            console.log('[TranscriptStore] loadTranscriptChunks() taskId =', taskId);
            const res = await TranscriptionsApi.getChunkedTranscription(
                taskId,
                skip,
                limit
            );
            if (res.successful) {
                const loadedChunkedTranscript = (
                    res as ResSuccess<ChunkedTranscription>
                ).data;
                console.log('[TranscriptStore] received chunks for taskId', taskId, loadedChunkedTranscript);
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
                            (timestamp) => formatTimestamp(timestamp)
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
                        ((!localStorage.getItem('cancelledWhileProcessing') ||
                            processingTranscript.currentState ===
                                TranscriptionState.completed_partially) &&
                            ![
                                TranscriptionState.queued,
                                TranscriptionState.in_progress,
                                TranscriptionState.processing_error,
                            ].includes(processingTranscript.currentState)) ||
                        new Date().getTime() -
                            processingTranscript.updateDate.getTime() >
                            30 * 60 * 1000
                    ) {
                        this.unwatchTranscriptionProcess();
                        localStorage.removeItem('cancelledWhileProcessing');
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
                const cancelledWhileProcessing = localStorage.getItem(
                    'cancelledWhileProcessing'
                );
                if (cancelledWhileProcessing) {
                    this.watchTranscriptionProcess(+cancelledWhileProcessing);
                    return +cancelledWhileProcessing;
                } else {
                    for (const transcription of this.transcriptsMap.values()) {
                        if (
                            [
                                TranscriptionState.queued,
                                TranscriptionState.in_progress,
                            ].includes(transcription.currentState) &&
                            new Date().getTime() -
                                transcription.updateDate.getTime() <
                                30 * 60 * 1000
                        ) {
                            this.watchTranscriptionProcess(transcription.id);
                            return transcription.id;
                        }
                    }
                }
            }
        },

        async cancelTranscriptionProcess(taskId?: number) {
            const id = taskId || this.processingTranscriptionId;
            if (id) {
                try {
                    const res = await TranscriptionsApi.cancelTranscriptionProcess(
                        id
                    );
                    if (res.successful) {
                        const transcript = this.transcriptsMap.get(id);
                        if (
                            transcript?.currentState ===
                            TranscriptionState.in_progress
                        ) {
                            localStorage.setItem(
                                'cancelledWhileProcessing',
                                `${id}`
                            );
                        } else if (
                            transcript?.currentState === TranscriptionState.queued
                        ) {
                            transcript.currentState = TranscriptionState.cancelled;
                            return;
                        }
                        this.isCancelling = true;
                    } else {
                        Notify.create({type: 'negative', message: 'Не удалось отменить задачу'});
                    }
                } catch (e) {
                    Notify.create({ type: 'negative', message: 'Не удалось отменить задачу' });
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
