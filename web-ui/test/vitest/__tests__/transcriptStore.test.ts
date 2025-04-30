import { describe, expect, it, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTranscriptStore } from 'src/stores/transcriptStore';
import { flushPromises } from '@vue/test-utils';
import { useUserInfoStore } from 'src/stores/userInfoStore';
import { getMockUser } from '../setup-file';
import { TranscriptionState } from 'src/models/transcripts';

describe('Стор транскрипций', () => {
    beforeEach(() => {
        setActivePinia(createPinia())
    })

    it('Должны подгружаться транскрипции только авторизованного пользователя', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true, 1);

        await transcriptStore.loadTranscriptions();
        expect(transcriptStore.transcriptsMap.size).toBe(0);
    });
    it('После корректной подгрузки транскрипции должны появиться в сторе', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true);

        await transcriptStore.loadTranscriptions();
        expect(transcriptStore.transcriptsMap.size).toBe(1);
    });
    it('После подгрузки чанков информация о них должна появиться в записи в словаре', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true);

        const date = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 0,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.completed,
            createDate: date,
            updateDate: date,
            description: 'string',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        expect(transcriptStore.transcriptsMap.get(1)?.chunks.length).toBe(0);
        await transcriptStore.loadTranscriptChunks(1);
        expect(transcriptStore.transcriptsMap.get(1)?.chunks.length).toBeGreaterThan(0);
    });
    it('После догрузки информации о транскрипции запись в словаре должна обновиться', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true);

        const date = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 0,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: null as any,
            createDate: date,
            updateDate: date,
            description: 'string',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        expect(transcriptStore.transcriptsMap.get(1)?.currentState).toBeNull();
        await transcriptStore.updateTranscriptionData(1);
        expect(transcriptStore.transcriptsMap.get(1)?.currentState).not.toBeNull();
    });
    it('При опрашивании состояния транскрипции каждые 2 секунды должны идти запросы на обновление иформации', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true);

        const date = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 0,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.in_progress,
            createDate: date,
            updateDate: date,
            description: 'string',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        const updateTranscriptionData = vi.spyOn(transcriptStore, 'updateTranscriptionData');
        transcriptStore.watchTranscriptionProcess(1);
        await flushPromises();
        await new Promise((resolve) => setTimeout(resolve, 2000));
        expect(updateTranscriptionData).toBeCalled();
        await flushPromises();
        await new Promise((resolve) => setTimeout(resolve, 2000));
        expect(updateTranscriptionData).toBeCalled();
    });
    it('Отмена обработки транскрипции, наподящейся в очереди, должна произойти немедленно', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true);

        const date = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 0,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.queued,
            createDate: date,
            updateDate: date,
            description: 'string',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        await transcriptStore.cancelTranscriptionProcess(1);
        expect(transcriptStore.transcriptsMap.get(1)?.currentState).toBe(TranscriptionState.cancelled);
    });
    it('При отмене уже начатой обработки id транскрипции должен быть сохранен в локальном хранилище', async () => {
        const transcriptStore = useTranscriptStore();
        const userInfoStore = useUserInfoStore();

        userInfoStore.userInfo = getMockUser(true);

        const date = new Date();
        transcriptStore.transcriptsMap.set(1, {
            id: 1,
            creatorId: 0,
            audioLenSecs: 100,
            chunkSizeSecs: 900,
            currentState: TranscriptionState.in_progress,
            createDate: date,
            updateDate: date,
            description: 'string',
            chunks: [],
            markXPositions: [],
            timeStampViews: [],
            chunksDurationArray: [],
        });

        await transcriptStore.cancelTranscriptionProcess(1);
        expect(localStorage.getItem(
            'cancelledWhileProcessing',
        )).toBe('1');
    });
});
