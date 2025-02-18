import { installQuasarPlugin } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

import { messages } from 'test/vitest/messages';
import { router } from 'test/vitest/setup-file';
import AuthPage from 'src/pages/AuthPage.vue';

installQuasarPlugin();

describe('Страница авторизации', () => {
    it('При нажатии на кнопку "Создать аккаунт" должен произойти переход на форму регистрации', async () => {
        const wrapper = mount(AuthPage, {
            global: {
                plugins: [router],
            },
        });

        const push = vi.spyOn(router, 'push');
        wrapper
            .get('[data-test="ui-testing-auth-page-switch-forms-btn"]')
            .trigger('click');
        expect(push).toBeCalledWith('/sign_up');
    });
    it('При нажатии на кнопку "Войти в существующий аккаунт" должен произойти переход на форму входа', async () => {
        const wrapper = mount(AuthPage, {
            props: {
                signUp: true,
            },
            global: {
                plugins: [router],
            },
        });

        const push = vi.spyOn(router, 'push');
        wrapper.get(
            '[data-test="ui-testing-auth-page-switch-forms-btn"]'
        ).trigger('click');
        expect(push).toBeCalledWith('/log_in');
    });

    const sendCorrectCreds = async (wrapper: any) => {
        const loginInput = wrapper.get(
            '[data-test="ui-testing-auth-page-login-input"]'
        );
        await loginInput.setValue('correct');

        const passwordInput = wrapper.get(
            '[data-test="ui-testing-auth-page-password-input"]'
        );
        await passwordInput.setValue('Correct1.1');
        await wrapper
            .get('[data-test="ui-testing-auth-page-form"]')
            .trigger('submit.prevent');

        await flushPromises();
    }

    const signUpCorrectly = async () => {
        const wrapper = mount(AuthPage, {
            props: {
                signUp: true,
            },
            global: {
                plugins: [router],
            },
        });

        await sendCorrectCreds(wrapper);
    }

    const expectValidationError = async (
        login: string,
        password: string,
        errorCaption: string
    ) => {
        const wrapper = mount(AuthPage);

        const loginInput = wrapper.get(
            '[data-test="ui-testing-auth-page-login-input"]'
        );
        await loginInput.setValue(login);

        const passwordInput = wrapper.get(
            '[data-test="ui-testing-auth-page-password-input"]'
        );
        await passwordInput.setValue(password);

        await wrapper
            .get('[data-test="ui-testing-auth-page-form"]')
            .trigger('submit.prevent');

        await flushPromises();

        const setupState = (wrapper.vm.$ as any).setupState;
        expect(setupState.errorMsg).toBe(messages.logInErrorMsg);
        expect(setupState.errorCaption).toBe(errorCaption);
    };

    const expectValidationSuccess = async (
        login: string,
        password: string,
    ) => {
        const wrapper = mount(AuthPage, {
            global: {
                plugins: [router],
            },
        });

        const loginInput = wrapper.get(
            '[data-test="ui-testing-auth-page-login-input"]'
        );
        await loginInput.setValue(login);

        const passwordInput = wrapper.get(
            '[data-test="ui-testing-auth-page-password-input"]'
        );
        await passwordInput.setValue(password);

        await wrapper
            .get('[data-test="ui-testing-auth-page-form"]')
            .trigger('submit.prevent');

        await flushPromises();

        const setupState = (wrapper.vm.$ as any).setupState;
        expect(setupState.errorMsg).toBeFalsy();
        expect(setupState.errorCaption).toBeFalsy();
    };

    it('Логин из 4 символов - должно быть выведено сообщение об ошибке', async () => {
        await expectValidationError(
            'wrng',
            'Password1.1',
            messages.incorrectLoginCaption
        );
    });
    it('Логин из 5 символов - ошибки быть не должно', async () => {
        await expectValidationSuccess(
            'login',
            'Password1.1',
        );
    });
    it('Логин из 65 символов - должно быть выведено сообщение об ошибке', async () => {
        await expectValidationError(
            'wrngggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg',
            'Password1.1',
            messages.incorrectLoginCaption
        );
    });
    it('Логин из 64 символов - ошибки быть не должно', async () => {
        await expectValidationSuccess(
            'gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggood',
            'Password1.1',
        );
    });
    it('В логине присутствуют символы не из латиницы - должно быть выведено сообщение об ошибке', async () => {
        await expectValidationError(
            'логин',
            'Password1.1',
            messages.incorrectLoginCaption
        );
    });
    it('Некорректный пароль - должно быть выведено сообщение об ошибке', async () => {
        await expectValidationError(
            'correct',
            'wrng',
            messages.incorrectPasswordCaption
        );
    });

    it('При успешной регистрации должен произойти автоматический вход', async () => {
        const push = vi.spyOn(router, 'push');
        await signUpCorrectly();

        expect(localStorage.getItem('accessToken')).toBeDefined();
        expect(localStorage.getItem('refreshToken')).toBeDefined();
        expect(push).toBeCalledWith('/transcripts');
    });

    const loginCorrectly = async () => {
        const wrapper = mount(AuthPage, {
            global: {
                plugins: [router],
            },
        });

        await sendCorrectCreds(wrapper);
    };

    it('При успешном входе должны быть сохранены токены аутентификации', async () => {
        await loginCorrectly();

        expect(localStorage.getItem('accessToken')).toBeDefined();
        expect(localStorage.getItem('refreshToken')).toBeDefined();
    });
    it('При успешном входе должен произойти переход на страницу транскрипций', async () => {
        const push = vi.spyOn(router, 'push');
        await loginCorrectly();
        expect(push).toBeCalledWith('/transcripts');
    });
});
