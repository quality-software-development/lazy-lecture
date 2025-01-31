<template>
    <q-item
        class="column items-end q-pt-md"
        clickable
        v-ripple
        :active="+route.params.taskId === transcription.id"
        active-class="ui-transcript-history-item-active"
        style="height: 90px"
        @click="router.push(`/transcripts/${transcription.id}`)"
    >
        <div class="row">
            <q-item-section style="margin-right: -20px" avatar>
                <q-icon :name="statusIconName" :color="statusIconColor" />
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
            </q-item-label>
        </q-item-section>
    </q-item>
    <q-separator />
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import {
    TranscriptionStatus,
    TranscriptionsMapElement,
} from 'src/models/transcripts';
import { date } from 'quasar';
import { computed } from 'vue';

const route = useRoute();
const router = useRouter();

const props = defineProps<{
    transcription: TranscriptionsMapElement;
}>();
defineOptions({
    name: 'TranscriptListItem',
});

const statusIconName = computed(() => {
    switch (props.transcription.currentState) {
        case TranscriptionStatus.queued:
            return 'schedule';
        case TranscriptionStatus.in_progress:
            return 'settings';
        case TranscriptionStatus.completed:
            return 'check_circle';
        case TranscriptionStatus.processing_fail:
        case TranscriptionStatus.cancelled:
            return 'cancel';
        default:
            return '';
    }
});
const statusIconColor = computed(() => {
    switch (props.transcription.currentState) {
        case TranscriptionStatus.queued:
            return 'grey';
        case TranscriptionStatus.in_progress:
            return 'warning';
        case TranscriptionStatus.completed:
            return 'positive';
        case TranscriptionStatus.processing_fail:
        case TranscriptionStatus.cancelled:
            return 'negative';
        default:
            return '';
    }
});
</script>

<style scoped>
.ui-transcript-history-item-active {
    background-color: #ebebeb;
    color: grey;
}
</style>
