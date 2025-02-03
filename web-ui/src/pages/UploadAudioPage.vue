<template>
    <q-page
        class="column items-center justify-center"
        v-if="
            userInfoStore.userInfo?.canInteract && !transcriptStore.isProcessing
        "
    >
        <p class="text-center text-grey-6">{{ hintText }}</p>
        <q-uploader
            ref="uploader"
            class="q-mx-md"
            label="MP-3"
            :url="`${api.getUri()}/upload-audiofile`"
            :headers="[
                { name: 'Authorization', value: `Bearer ${accessToken}` },
            ]"
            accept=".mp3"
            field-name="audiofile"
            max-file-size="209715200"
            @added="handleAudioAdd"
            @removed="hintText = hintBeforeAdd"
            @uploaded="handleAudioUpload"
        />
    </q-page>
    <q-page
        v-else-if="
            userInfoStore.userInfo?.canInteract && transcriptStore.isProcessing
        "
        class="fit column items-center justify-center"
    >
        <IconMessageItem icon="settings">
            Идёт обработка аудио...
        </IconMessageItem>
    </q-page>
    <q-page v-else class="fit column items-center justify-center">
        <IconMessageItem icon="file_upload_off">
            <p class="text-h6 text-grey-5 text-center">
                Нет доступа к обработке аудио.<br />Запросите доступ у
                <a href="https://t.me/ll_requests">администраторов</a>
            </p>
        </IconMessageItem>
    </q-page>
</template>

<script setup lang="ts">
import { useUserInfoStore } from 'src/stores/userInfoStore';
import { useTranscriptStore } from 'src/stores/transcriptStore';
import { api } from 'src/boot/axios';
import { onMounted, ref, useTemplateRef } from 'vue';
import IconMessageItem from 'src/components/IconMessageItem.vue';
import { QUploader, useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
const userInfoStore = useUserInfoStore();
const transcriptStore = useTranscriptStore();
const $q = useQuasar();
const router = useRouter();

const accessToken = ref(localStorage.getItem('accessToken'));

const hintBeforeAdd = 'Перетащите аудио в поле или нажмите на плюс';
const hintAfterAdd = 'Нажмите на облако для отправки аудио на обработку';
const hintText = ref(hintBeforeAdd);

const tooltipsMap: any = {
    clear_all: 'Очистить поле',
    cloud_upload: 'Отправить аудио на обработку',
    close: 'Очистить поле',
};

const uploader = useTemplateRef<QUploader>('uploader');

const handleAudioAdd = (files: readonly any[]) => {
    const audio = document.createElement('audio');
    audio.preload = 'metadata';
    audio.onloadedmetadata = () => {
        URL.revokeObjectURL(audio.src);
        if (audio.duration < 10 || audio.duration > 7200) {
            if (audio.duration < 10) {
                $q.notify({
                    type: 'negative',
                    icon: 'error',
                    position: 'bottom-right',
                    message: 'Длина аудио должна быть больше 10 секунд.',
                    actions: [{ icon: 'close', color: 'white', round: true }],
                });
            } else if (audio.duration > 7200) {
                $q.notify({
                    type: 'negative',
                    icon: 'error',
                    position: 'bottom-right',
                    message: 'Длина аудио должна быть меньше 2 часов.',
                    actions: [{ icon: 'close', color: 'white', round: true }],
                });
            }
            uploader.value?.removeFile(files[0]);
        }
    }
    audio.src = URL.createObjectURL(files[0]);

    hintText.value = hintAfterAdd;
    setTimeout(() => {
        for (const btnIcon of Array.from(
            document.querySelectorAll('.q-uploader .q-icon')
        )) {
            btnIcon.setAttribute('title', tooltipsMap[btnIcon.innerHTML]);
        }
    });
};

const handleAudioUpload = async () => {
    await transcriptStore.loadTranscriptions();
    const id = transcriptStore.checkProcessingTranscription();
    if (id) {
        router.push(`/transcripts/${id}`);
    }
};

onMounted(() => {
    document
        .querySelector('.q-uploader__input')
        ?.setAttribute('title', 'Добавить аудиофайл');
});
</script>

<style scoped>
a {
    color: gray;
}
a:visited {
    color: lightgray;
}
</style>
