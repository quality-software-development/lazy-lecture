import { installQuasarPlugin } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import AuthPage from 'src/pages/AuthPage.vue';

installQuasarPlugin();

describe('Страница авторизации', () => {
    it('При регистрации заголовок формы должен быть "Регистрация"', async () => {
        const wrapper = mount(AuthPage, {
            props: {
                signUp: true,
            },
        });
        const authPageHeader = wrapper.get('[data-test="ui-testing-auth-page-header"]');
        expect(authPageHeader.text()).toBe('Регистрация');
    });
    it('При входе заголовок формы должен быть "Вход"', async () => {
        const wrapper = mount(AuthPage);
        const authPageHeader = wrapper.get('[data-test="ui-testing-auth-page-header"]');
        expect(authPageHeader.text()).toBe('Вход');
    });
});
