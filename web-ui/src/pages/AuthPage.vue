<template>
    <div class="fullscreen row items-center justify-evenly">
        <q-card
            class="q-py-xl q-mx-lg column items-center justify-evenly"
            style="height: 500px; width: 500px"
        >
            <div class="text-h3">
                {{ props.signUp ? 'Регистрация' : 'Вход' }}
            </div>
            <q-form
                ref="form"
                style="height: 50%; width: 50%"
                @submit="submitHandler"
            >
                <q-input
                    :rules="[(val) => !!val || 'Введите логин']"
                    v-model="login"
                    label="Имя пользователя"
                />
                <q-input
                    :rules="[(val) => !!val || 'Введите пароль']"
                    v-model="password"
                    type="password"
                    label="Пароль"
                />
                <q-btn class="q-mt-lg full-width" color="primary" type="submit"
                    >{{ props.signUp ? 'Зарегистрироваться' : 'Войти' }}
                </q-btn>
            </q-form>
            <div v-if="errorMsg" class="ui-auth-error row items-center q-mt-sm">
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
            >
                {{ props.signUp ? 'Войти в существующий' : 'Создать' }} аккаунт
            </q-btn>
        </q-card>
    </div>
</template>

<script setup lang="ts">
import { ref, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import { AuthApi } from 'src/api/auth';
import { ResError } from 'src/models/responses';
import { QForm } from 'quasar';
const router = useRouter();
const props = defineProps(['signUp']);

const login = ref('');
const password = ref('');
const errorMsg = ref('');
const errorCaption = ref('');

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
