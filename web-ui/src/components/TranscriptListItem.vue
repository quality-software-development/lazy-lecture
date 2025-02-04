<template>
    <q-item
        class="column items-end q-pt-md"
        clickable
        v-ripple
        :active="+route.params.taskId === transcription.id"
        active-class="ui-transcript-history-item-active"
        style="height: 110px"
        @click="router.push(`/transcripts/${transcription.id}`)"
    >
        <div class="row">
            <q-item-section avatar :title="hint">
                <q-icon :name="statusIconName" :color="statusIconColor" />
            </q-item-section>
            <q-item-section v-if="isExtraCogVisible" avatar>
                <q-icon name="settings" color="warning" />
            </q-item-section>
            <q-item-section class="text-grey-6">{{
                date.formatDate(transcription.updateDate, 'D MMM HH:mm', {
                    monthsShort: [
                        'янв',
                        'фев',
                        'мар',
                        'апр',
                        'мая',
                        'июн',
                        'июл',
                        'авг',
                        'сен',
                        'окт',
                        'ноя',
                        'дек',
                    ],
                })
            }}</q-item-section>
        </div>

        <q-item-section class="q-ml-md">
            <q-item-label
                style="
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                "
            >
                {{
                    transcription.description || transcription.chunks?.[0]?.text
                }}
                <div
                    v-if="
                        !transcription.description &&
                        !transcription.chunks?.[0]?.text
                    "
                    class="text-italic"
                >
                    Нет текста.
                </div>
            </q-item-label>
        </q-item-section>

        <div
            v-if="+route.params.taskId === transcription.id"
            class="text-italic text-grey-6 text-caption"
        >
            {{
                `обработано ${
                    transcription.chunks.length
                        ? formatTimestamp(
                              transcription.chunksDurationArray[
                                  transcription.chunksDurationArray.length - 1
                              ] < transcription.audioLenSecs
                                  ? transcription.chunksDurationArray[
                                        transcription.chunksDurationArray
                                            .length - 1
                                    ]
                                  : transcription.audioLenSecs
                          )
                        : '00:00:00'
                } из ${formatTimestamp(transcription.audioLenSecs)}`
            }}
        </div>
    </q-item>
    <q-separator />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { TranscriptionsMapElement } from 'src/models/transcripts';
import { date } from 'quasar';
import { formatTimestamp } from 'src/composables/formatTimestamp';
import { computed, ref, watch } from 'vue';
import { useTranscriptStore } from 'src/stores/transcriptStore';
const transcriptStore = useTranscriptStore();

const route = useRoute();
const router = useRouter();

const props = defineProps<{
    transcription: TranscriptionsMapElement;
}>();
defineOptions({
    name: 'TranscriptListItem',
});

const statusIconName = computed(
    () =>
        [
            'schedule',
            'settings',
            'error',
            'check_circle',
            'block',
            'cancel',
            'block',
        ][props.transcription.currentState]
);
const statusIconColor = computed(
    () =>
        [
            'grey',
            'warning',
            'negative',
            'positive',
            'black',
            'negative',
            'black',
        ][props.transcription.currentState]
);
const hint = computed(
    () =>
        [
            'В очереди',
            'В обработке',
            'Ошибка при обработке',
            'Завершено',
            'Завершено частично',
            'Завершено с ошибкой',
            'Отменено',
        ][props.transcription.currentState]
);
const cancelledWhileProcessing = ref(
    localStorage.getItem('cancelledWhileProcessing')
);
const isExtraCogVisible = computed(
    () =>
        ((cancelledWhileProcessing.value &&
            +cancelledWhileProcessing.value === props.transcription.id) ||
            transcriptStore.isTranscriptCancelling(props.transcription.id)) &&
        statusIconName.value !== 'settings'
);
watch(
    () => transcriptStore.processsingTicks,
    () => {
        cancelledWhileProcessing.value = localStorage.getItem(
            'cancelledWhileProcessing'
        );
    }
);
</script>

<style scoped>
.ui-transcript-history-item-active {
    background-color: #ebebeb;
    color: grey;
}
.q-item__section--avatar {
    margin-right: -20px;
}
</style>
