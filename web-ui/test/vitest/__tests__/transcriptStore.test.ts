import {createPinia, setActivePinia} from 'pinia';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {useTranscriptStore} from 'src/stores/transcriptStore';
import {useUserInfoStore} from 'src/stores/userInfoStore';
import {getMockUser, ok} from '../setup-file';
import {TranscriptionState} from 'src/models/transcripts';

vi.mock('src/api/transcripts', () => ({
    TranscriptionsApi: {
        getTranscriptions: vi.fn().mockResolvedValue(ok({
            page: 1,
            pages: 1,
            size: 1,
            total: 1,
            transcriptions: [{
                id: 1,
                creatorId: 1,
                audioLenSecs: 100,
                chunkSizeSecs: 900,
                currentState: TranscriptionState.completed,
                createDate: new Date(),
                updateDate: new Date(),
                description: 'test-audio.mp3',
            }],
        })),
        getChunkedTranscription: vi.fn().mockResolvedValue(ok({
            taskId: 1,
            chunks: [{index: 0, duration: 900, text: 'Mock chunk text.'}],
        })),
        getTranscriptionInfo: vi.fn().mockResolvedValue(ok({
            id: 1,
            creatorId: 1,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.completed,
            createDate: new Date(),
            updateDate: new Date(),
            description: 'test-audio.mp3',
        })),
        cancelTranscriptionProcess: vi.fn().mockResolvedValue(ok(null)),
    }
}));

describe('Стор транскрипций', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        vi.clearAllMocks();
    });

    it('Загружаются только транскрипции текущего пользователя', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 2); // пользователь ≠ creatorId

        await transcriptStore.loadTranscriptions();
        expect(transcriptStore.transcriptsMap.size).toBe(0);
    });

    it('Загруженные транскрипции появляются в сторе', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 1);

        await transcriptStore.loadTranscriptions();
        expect(transcriptStore.transcriptsMap.has(1)).toBe(true);
    });

    it('После загрузки чанков — они сохраняются в transcript', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 1);

        const now = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 1,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.completed,
            createDate: now,
            updateDate: now,
            description: 'test',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        await transcriptStore.loadTranscriptChunks(1);
        expect(transcriptStore.transcriptsMap.get(1)?.chunks.length).toBeGreaterThan(0);
    });

    it('После обновления info — данные в transcript обновляются', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 1);

        const now = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 1,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: null as any,
            createDate: now,
            updateDate: now,
            description: 'test',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        await transcriptStore.updateTranscriptionData(1);
        expect(transcriptStore.transcriptsMap.get(1)?.currentState).not.toBeNull();
    });

    it('watchTranscriptionProcess вызывает обновления каждые 2 секунды', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 1);

        const now = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 1,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.in_progress,
            createDate: now,
            updateDate: now,
            description: 'test',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        const spy = vi.spyOn(transcriptStore, 'updateTranscriptionData');
        transcriptStore.watchTranscriptionProcess(1);

        await new Promise(resolve => setTimeout(resolve, 2100));
        expect(spy).toHaveBeenCalled();
        transcriptStore.unwatchTranscriptionProcess(); // Clean up
    });

    it('Если в очереди — обработка отменяется сразу', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 1);

        const now = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 1,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.queued,
            createDate: now,
            updateDate: now,
            description: 'test',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        await transcriptStore.cancelTranscriptionProcess(1);
        expect(transcriptStore.transcriptsMap.get(1)?.currentState).toBe(TranscriptionState.cancelled);
    });

    it('Если в процессе — id сохраняется в локальное хранилище', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true, 1);

        const now = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 1,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.in_progress,
            createDate: now,
            updateDate: now,
            description: 'test',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        await transcriptStore.cancelTranscriptionProcess(1);
        expect(localStorage.getItem('cancelledWhileProcessing')).toBe('1');
    });
});
