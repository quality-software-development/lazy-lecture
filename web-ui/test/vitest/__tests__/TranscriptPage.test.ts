import { installQuasarPlugin } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

import { createTestingPinia } from '@pinia/testing';
import { getMockUser, router } from 'test/vitest/setup-file';
import TranscriptPage from 'src/pages/TranscriptPage.vue';

import { useTranscriptStore } from 'src/stores/transcriptStore';
import { TranscriptionState } from 'src/models/transcripts';
import { useUserInfoStore } from 'src/stores/userInfoStore';
installQuasarPlugin();

describe('Страница просмотра транскрипции', () => {
    it('При открытии экрана транскрипции должны подгружаться её чанки', async () => {
        vi.mock('vue-router', () => ({
            useRoute: vi.fn().mockReturnValue({ params: { taskId: '1' }, hash: '' }),
            useRouter: vi.fn().mockReturnValue(router)
        }));

        const testingPinia = createTestingPinia({
            stubActions: false,
            createSpy: vi.fn,
        });

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
                {
                    duration: 900,
                    index: 0,
                    text: 'Mock chunk text'
                }
            ],
            markXPositions: [0],
            timeStampViews: ['00:00:00'],
            chunksDurationArray: [900],
        });
        const loadTranscriptChunks = vi.spyOn(transcriptStore, 'loadTranscriptChunks');
        loadTranscriptChunks.mockImplementation(vi.fn as any);

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);

        mount(TranscriptPage, {
            global: {
                plugins: [
                    testingPinia,
                ],
            },
        });

        expect(loadTranscriptChunks).toBeCalled();
    });
});
