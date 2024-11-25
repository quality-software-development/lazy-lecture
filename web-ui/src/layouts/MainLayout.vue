<template>
    <q-layout view="lHh Lpr lFf">
        <q-header elevated>
            <q-toolbar>
                <q-btn
                    flat
                    dense
                    round
                    icon="menu"
                    aria-label="Menu"
                    @click="toggleLeftDrawer"
                />
                <q-toolbar-title> Lazy Lecture </q-toolbar-title>
            </q-toolbar>
        </q-header>

        <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
            <q-list>
                <q-item-label header> История </q-item-label>
                <q-separator />
                <TranscriptListItem
                    v-for="transcript in transcriptStore.transcriptsMap.values()"
                    :key="transcript.taskId"
                    v-bind="transcript"
                />
            </q-list>
        </q-drawer>

        <q-page-container>
            <router-view />
        </q-page-container>
    </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TranscriptListItem from 'src/components/TranscriptListItem.vue';
import { useTranscriptStore } from 'src/stores/transcriptStore';

defineOptions({
    name: 'MainLayout',
});

const transcriptStore = useTranscriptStore();
await transcriptStore.loadTranscripts(0, 100);

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
    leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>
