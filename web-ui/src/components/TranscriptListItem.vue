<template>
    <q-item
        class="column items-end q-pt-md"
        clickable
        v-ripple
        style="height: 90px"
    >
        <div class="row">
            <q-item-section style="margin-right: -20px" avatar>
                <q-icon :name="statusIconName" :color="statusIconColor" />
            </q-item-section>
            <q-item-section class="text-grey-6">{{
                date.formatDate(timeStamp, 'D MMM HH:mm')
            }}</q-item-section>
        </div>

        <q-item-section class="q-ml-md">
            <q-item-label
                style="
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                "
                >{{ text }}</q-item-label
            >
        </q-item-section>
    </q-item>
    <q-separator />
</template>

<script setup lang="ts">
import { TranscriptStatus } from 'src/models/transcripts';
import { date } from 'quasar';

interface TranscriptListItemProps {
    text: string;
    timeStamp: Date;
    status: TranscriptStatus;
}

const props = defineProps<TranscriptListItemProps>();
defineOptions({
    name: 'TranscriptListItem',
});

let statusIconName: string, statusIconColor: string;

switch (props.status) {
    case TranscriptStatus.QUEUED:
        statusIconName = 'schedule';
        statusIconColor = 'grey';
        break;
    case TranscriptStatus.IN_PROGRESS:
        statusIconName = 'settings';
        statusIconColor = 'warning';
        break;
    case TranscriptStatus.COMPLETED:
        statusIconName = 'check_circle';
        statusIconColor = 'positive';
        break;
    case TranscriptStatus.REJECTED:
        statusIconName = 'cancel';
        statusIconColor = 'negative';
}
</script>
