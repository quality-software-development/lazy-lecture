<template>
    <q-page class="row items-center justify-evenly">
        <q-btn
            class="q-pa-xl"
            outline
            flat
            color="primary"
            stack
            @click="uploadAudio"
        >
            <q-icon
                class="q-mb-lg"
                name="upload_file"
                color="primary"
                size="200px"
            />
            <div class="text-h4">Перевести аудио в текст</div>
        </q-btn>
    </q-page>
</template>

<script setup lang="ts">
const uploadAudio = () => {
    console.log('UPLOAD');
};
</script>
