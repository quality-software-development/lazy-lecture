<template>
    <div class="fullscreen row items-center justify-evenly">
        <q-card
            class="q-py-xl q-mx-lg column items-center justify-evenly"
            style="height: 500px; width: 500px"
        >
            <div class="text-h3" data-test="ui-testing-auth-page-header">
                {{ props.signUp ? 'Регистрация' : 'Вход' }}
            </div>
            <q-form
                ref="form"
                style="height: 50%; width: 50%"
                @submit="submitHandler"
                data-test="ui-testing-auth-page-form"
            >
                <q-input
                    :rules="[(val) => !!val || 'Введите логин']"
                    v-model="login"
                    label="Имя пользователя"
                    data-test="ui-testing-auth-page-login-input"
                />
                <q-input
                    :rules="[(val) => !!val || 'Введите пароль']"
                    v-model="password"
                    :type="isPassword ? 'password' : 'text'"
                    label="Пароль"
                    data-test="ui-testing-auth-page-password-input"
                >
                    <template v-slot:append>
                        <q-icon
                            :name="isPassword ? 'visibility_off' : 'visibility'"
                            class="cursor-pointer"
                            @click="isPassword = !isPassword"
                        />
                    </template>
                </q-input>
                <q-btn
                    class="q-mt-lg full-width"
                    color="primary"
                    type="submit"
                    data-test="ui-testing-auth-page-submit-btn"
                >
                    {{ props.signUp ? 'Зарегистрироваться' : 'Войти' }}
                </q-btn>
            </q-form>
            <div
                v-if="errorMsg"
                class="ui-auth-error row items-center q-mt-sm"
                data-test="ui-testing-auth-page-error-msg"
            >
                <q-icon name="sym_o_error" class="q-mr-xs" />
                {{ errorMsg }}
                <q-tooltip
                    v-if="errorCaption"
                    class="bg-negative text-body2"
                    max-width="40%"
                    :offset="[10, 10]"
                >
                    {{ errorCaption }}
                </q-tooltip>
            </div>
            <q-btn
                flat
                class="q-mt-lg"
                color="primary"
                @click="formChangeHandler"
                data-test="ui-testing-auth-page-switch-forms-btn"
            >
                {{ props.signUp ? 'Войти в существующий' : 'Создать' }} аккаунт
            </q-btn>
        </q-card>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import { AuthApi } from 'src/api/auth';
import { ResError } from 'src/models/responses';
import { QForm } from 'quasar';
const router = useRouter();
const props = defineProps(['signUp']);

const accessToken = computed(() => localStorage.getItem('accessToken'))
const refreshToken = computed(() => localStorage.getItem('refreshToken'))

const login = ref('');
const password = ref('');
const errorMsg = ref('');
const errorCaption = ref('');
const isPassword = ref(true);

const form = useTemplateRef<QForm>('form');

const setErrors = (err: ResError) => {
    errorMsg.value = (err as ResError)?.message;
    errorCaption.value = (err as ResError)?.caption || '';
};

const submitHandler = async () => {
    if (props.signUp) {
        const signUpRes = await AuthApi.signUp(login.value, password.value);
        if (!signUpRes?.successful) {
            setErrors(signUpRes as ResError);
            return;
        }
    }
    const logInRes = await AuthApi.logIn(login.value, password.value);
    if (logInRes?.successful) {
        router.push('/transcripts');
    } else {
        setErrors(logInRes as ResError);
    }
};
const formChangeHandler = () => {
    login.value = '';
    password.value = '';
    errorMsg.value = '';
    errorCaption.value = '';
    router.push(props.signUp ? '/log_in' : '/sign_up');
    setTimeout(() => form.value?.resetValidation());
};
</script>

<style scoped lang="scss">
.ui-auth-error {
    color: $negative;
}
</style>
