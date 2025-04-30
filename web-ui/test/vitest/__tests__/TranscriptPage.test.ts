import {installQuasarPlugin} from '@quasar/quasar-app-extension-testing-unit-vitest';
import {mount} from '@vue/test-utils';
import {describe, expect, it, vi} from 'vitest';
import {createTestingPinia} from '@pinia/testing';
import {setActivePinia} from 'pinia';
import {getMockUser, router} from 'test/vitest/setup-file';
import TranscriptPage from 'src/pages/TranscriptPage.vue';
import {useTranscriptStore} from 'src/stores/transcriptStore';
import {TranscriptionState} from 'src/models/transcripts';
import {useUserInfoStore} from 'src/stores/userInfoStore';

installQuasarPlugin();

describe('Страница просмотра транскрипции', () => {
    it('При открытии экрана транскрипции должны подгружаться её чанки', async () => {
        // 1) Мокаем vue-router перед созданием Pinia
        vi.mock('vue-router', () => ({
            useRoute: vi.fn().mockReturnValue({params: {taskId: '1'}, hash: ''}),
            useRouter: vi.fn().mockReturnValue(router),
        }));

        // 2) Создаём и активируем Testing Pinia
        const pinia = createTestingPinia({
            stubActions: false,
            createSpy: vi.fn,
        });
        setActivePinia(pinia);

        // 3) Конфигурируем store из того же Pinia
        const transcriptStore = useTranscriptStore();
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
            chunks: [
                {duration: 900, index: 0, text: 'Mock chunk text'}
            ],
            markXPositions: [0],
            timeStampViews: ['00:00:00'],
            chunksDurationArray: [900],
        });

        // 4) Шпионим на loadTranscriptChunks
        const loadSpy = vi.spyOn(transcriptStore, 'loadTranscriptChunks')
            .mockResolvedValue(undefined as any);

        // 5) Мокаем авторизованного пользователя
        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);

        // 6) Монтируем компонент с тем же Pinia
        mount(TranscriptPage, {
            global: {
                plugins: [pinia],
            },
        });

        // 7) Проверяем вызов метода
        expect(loadSpy).toHaveBeenCalledWith(1);
    });
});
