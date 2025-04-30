import {installQuasarPlugin} from '@quasar/quasar-app-extension-testing-unit-vitest';
import {flushPromises, mount} from '@vue/test-utils';
import {describe, expect, it, vi} from 'vitest';

import {createTestingPinia} from '@pinia/testing';
import {useUserInfoStore} from 'src/stores/userInfoStore';
import {useTranscriptStore} from 'src/stores/transcriptStore';
import UploadAudioPage from 'src/pages/UploadAudioPage.vue';

import {Notify} from 'quasar';
import {getMockUser, router} from 'test/vitest/setup-file';

installQuasarPlugin({plugins: {Notify}});

describe('Страница отправки аудио на обработку', () => {
    it('Обработка аудио должна быть недоступна, если у пользователя нет соответствующих прав', async () => {
        const wrapper = mount(UploadAudioPage, {
            global: {
                plugins: [createTestingPinia({createSpy: vi.fn})],
            },
        });

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(false);
        await flushPromises();

        expect(wrapper.vm.$refs.uploader).toBeUndefined();
        expect(wrapper.get('[data-test="ui-testing-upload-audio-page-forbidden-p"]').text())
            .toBe('Нет доступа к обработке аудио.Запросите доступ у администраторов');
    });

    it('Обработка аудио должна быть недоступна, если уже есть аудио в обработке', async () => {
        const wrapper = mount(UploadAudioPage, {
            global: {
                plugins: [createTestingPinia({createSpy: vi.fn})],
            },
        });

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);
        const transcriptStore = useTranscriptStore();
        transcriptStore.isProcessing = true;
        await flushPromises();

        expect(wrapper.vm.$refs.uploader).toBeUndefined();
        expect(wrapper.get('[data-test="ui-testing-upload-audio-page-processing-p"]').text())
            .toBe('Нельзя загрузить - идёт обработка аудио.');
    });

    it('Аудио тяжелее 200Мб - должно быть выведено сообщение об ошибке', async () => {
        const wrapper = mount(UploadAudioPage, {
            global: {
                plugins: [createTestingPinia({createSpy: vi.fn})],
            },
        });

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);
        await flushPromises();

        const notify = vi.spyOn((wrapper.vm as any).$q, 'notify');

        const audio = new File(
            [new ArrayBuffer(200 * 1024 * 1024 + 1)],
            'large-test.mp3',
            {type: 'audio/mpeg'}
        );

        await wrapper.vm.handleAudioAdd([audio]);
        expect(notify).toHaveBeenCalledWith({
            type: 'negative',
            icon: 'error',
            position: 'bottom-right',
            message: 'Размер аудио должен быть меньше 200 Мбайт.',
            actions: [{icon: 'close', color: 'white', round: true}],
        });
    });

    it('При отправке аудио должен начаться опрос состояния обработки', async () => {
        const wrapper = mount(UploadAudioPage, {
            global: {
                plugins: [
                    router,
                    createTestingPinia({
                        stubActions: false,
                        createSpy: vi.fn,
                    }),
                ],
            },
        });

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);
        await flushPromises();

        await wrapper.vm.handleAudioUpload();
        expect(useTranscriptStore().checkProcessingTranscription).toBeCalled();
    });

    it('После начала опроса состояния обработки должен произойти переход на страницу новой транскрипции', async () => {
        const wrapper = mount(UploadAudioPage, {
            global: {
                plugins: [
                    router,
                    createTestingPinia({
                        stubActions: false,
                        createSpy: vi.fn,
                    }),
                ],
            },
        });

        const userInfoStore = useUserInfoStore();
        userInfoStore.userInfo = getMockUser(true);
        await flushPromises();

        const push = vi.spyOn(router, 'push');
        await wrapper.vm.handleAudioUpload();
        expect(push).toBeCalledWith('/transcripts/1');
    });
});
