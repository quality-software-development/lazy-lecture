import { installQuasarPlugin } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

import { createTestingPinia } from '@pinia/testing';
import { getMockUser, router } from 'test/vitest/setup-file';
import TranscriptPage from 'src/pages/TranscriptPage.vue';

import { api } from 'src/boot/axios';
import { useTranscriptStore } from 'src/stores/transcriptStore';
import MainLayout from 'src/layouts/MainLayout.vue';
import App from 'src/App.vue';
import { TranscriptionState } from 'src/models/transcripts';
import { useRoute } from 'vue-router';
import { useUserInfoStore } from 'src/stores/userInfoStore';
installQuasarPlugin();

describe('Страница просмотра транскрипции', () => {
    it('Для существующей транскрипции открывается её прогресс-бар и текст', async () => {

        vi.mock('vue-router', () => ({
            useRoute: vi.fn().mockReturnValue({ params: { taskId: '1' }, hash: '' }),
            useRouter: vi.fn().mockReturnValue(router)
        }));

        const wrapper = mount(TranscriptPage, {
            global: {
                plugins: [
                    createTestingPinia({
                        stubActions: false,
                        createSpy: vi.fn,
                    }),
                ],
            },
        });

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);

        const transcriptStore = useTranscriptStore();
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
        await new Promise((resolve) => setTimeout(resolve, 1000));

        console.log(wrapper.text());
        // const transcriptStore = useTranscriptStore();
        // const date = new Date();

    });
});
