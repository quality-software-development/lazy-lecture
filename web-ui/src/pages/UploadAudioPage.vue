<template>
    <q-page
        class="column items-center justify-center"
        v-if="
            userInfoStore.userInfo?.canInteract && !transcriptStore.isProcessing
        "
    >
        <p class="text-center text-grey-6">{{ hintText }}</p>
        <q-uploader
            label="MP-3"
            :url="`${api.getUri()}/upload-audiofile`"
            :headers="[
                { name: 'Authorization', value: `Bearer ${accessToken}` },
            ]"
            accept=".mp3"
            field-name="audiofile"
            @added="handleAudioAdd"
            @removed="hintText = hintBeforeAdd"
            @uploaded="handleAudioUpload"
            class="q-mx-md"
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
                <a href="hhttps://t.me/quakumei">администратороа</a>
            </p>
        </IconMessageItem>
    </q-page>
</template>

<script setup lang="ts">
import { useUserInfoStore } from 'src/stores/userInfoStore';
import { useTranscriptStore } from 'src/stores/transcriptStore';
import { api } from 'src/boot/axios';
import { onMounted, ref } from 'vue';
import IconMessageItem from 'src/components/IconMessageItem.vue';
const userInfoStore = useUserInfoStore();
const transcriptStore = useTranscriptStore();

const accessToken = ref(localStorage.getItem('accessToken'));

const hintBeforeAdd = 'Перетащите аудио в поле или нажмите на плюс';
const hintAfterAdd = 'Нажмите на облако для отправки аудио на обработку';
const hintText = ref(hintBeforeAdd);

const tooltipsMap: any = {
    clear_all: 'Очистить поле',
    cloud_upload: 'Отправить аудио на обработку',
    close: 'Очистить поле',
};

const handleAudioAdd = () => {
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
    transcriptStore.checkProcessingTranscription();
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
