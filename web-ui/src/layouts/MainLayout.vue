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
                <q-item v-if="userInfoStore.userInfo" clickable v-ripple>
                    <q-item-section avatar class="q-pr-none">
                        <q-icon name="account_circle" />
                    </q-item-section>
                    <q-item-section>
                        {{ userInfoStore.userInfo.username }}
                    </q-item-section>
                    <q-menu>
                        <q-list>
                            <q-item clickable v-close-popup @click="logOut">
                                <q-item-section avatar class="q-pr-none">
                                    <q-icon name="logout" />
                                </q-item-section>
                                <q-item-section> Выход </q-item-section>
                            </q-item>
                        </q-list>
                    </q-menu>
                </q-item>
            </q-toolbar>
        </q-header>

        <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
            <q-list>
                <div
                    style="
                        position: sticky;
                        top: 0;
                        z-index: 1;
                        background-color: white;
                    "
                >
                    <q-item-label header> История </q-item-label>
                    <q-separator />
                </div>
                <div v-if="transcriptStore.transcriptsMap.size > 0">
                    <TranscriptListItem
                        v-for="transcript in transcriptStore.transcriptsMap.values()"
                        :key="transcript.id"
                        :transcription="transcript"
                    />
                </div>
                <p class="q-ma-md text-grey-6" v-else>Нет транскрипций.</p>
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
import { useUserInfoStore } from 'src/stores/userInfoStore';
import { useRouter } from 'vue-router';
const router = useRouter();

defineOptions({
    name: 'MainLayout',
});

const userInfoStore = useUserInfoStore();
const transcriptStore = useTranscriptStore();
await transcriptStore.loadTranscriptions();
transcriptStore.checkProcessingTranscription();

const leftDrawerOpen = ref(false);

const toggleLeftDrawer = () => {
    leftDrawerOpen.value = !leftDrawerOpen.value;
};

const logOut = () => {
    userInfoStore.clearUserInfo();
    transcriptStore.transcriptsMap.clear();
    transcriptStore.unwatchTranscriptionProcess();
    router.push({ path: '/log_in' });
};
</script>

<style scoped>
.q-item__section--avatar {
    margin-right: -24px;
}
</style>
