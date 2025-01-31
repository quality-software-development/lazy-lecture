<template>
    <Suspense>
        <router-view />
    </Suspense>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { useTranscriptStore } from './stores/transcriptStore';
const $q = useQuasar();

useTranscriptStore().$onAction(({ onError }) => {
    onError((error: any) => {
        $q.notify({
            type: 'negative',
            position: 'bottom-right',
            message: error,
            actions: [{ icon: 'close', color: 'white', round: true }],
        });
    });
});

defineOptions({
    name: 'App',
});
</script>
