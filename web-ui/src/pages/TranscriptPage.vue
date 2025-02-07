<template>
    <div v-if="currentTranscript" :class="showStateIconMessage ? 'column' : ''">
        <div class="ui-transcript-page-progress-container">
            <div
                class="ui-trancscript-page-progress-bar q-pa-lg q-pb-sm q-px-xl"
            >
                <svg
                    class="ui-trancscript-page-progress-bar-marks"
                    width="100%"
                    :height="markHeight"
                    ref="marks"
                >
                    <rect
                        v-for="(xPos, idx) of relativeMarkPositions"
                        :class="`ui-progress-mark${
                            isCurrentTranscriptProcessing ||
                            isCurrentTranscriptCancelling
                                ? '-processing'
                                : currentTranscript.chunks[idx].text
                                ? '-complete'
                                : '-empty'
                        }`"
                        :rect-idx="idx"
                        :key="idx"
                        :x="xPos"
                        :width="markWidth"
                        :height="markHeight"
                        @click="handleMarkClick(idx)"
                    />
                </svg>
                <q-linear-progress
                    size="md"
                    :stripe="
                        isCurrentTranscriptProcessing ||
                        isCurrentTranscriptCancelling
                    "
                    :value="
                        (currentTranscript.chunksDurationArray[
                            currentTranscript.chunksDurationArray.length - 1
                        ] || 0) / currentTranscript.audioLenSecs
                    "
                    :color="
                        isCurrentTranscriptProcessing ||
                        isCurrentTranscriptCancelling
                            ? 'warning'
                            : 'primary'
                    "
                    animation-speed="100"
                />
            </div>
            <div class="row q-mb-sm">
                <span
                    :class="`ui-transcript-page-progress-timestamp${
                        currentTranscript.chunks[idx].text ? '' : ' empty'
                    }`"
                    v-for="(
                        chunkTimeStamp, idx
                    ) of currentTranscript.timeStampViews"
                    :key="idx"
                    :span-idx="idx"
                    @click="handleMarkClick(idx)"
                >
                    {{ chunkTimeStamp }}
                </span>
            </div>
            <q-btn
                class="full-width"
                v-if="
                    isCurrentTranscriptProcessing ||
                    currentTranscript.currentState === TranscriptionState.queued
                "
                flat
                square
                color="negative"
                @click="
                    transcriptStore.cancelTranscriptionProcess(
                        currentTranscript.id
                    )
                "
            >
                Отменить обработку
            </q-btn>
            <p
                v-if="isCurrentTranscriptCancelling"
                class="text-grey-6 text-center"
            >
                Обработка отменена. Текущий фрагмент будет обработан.
            </p>
            <q-separator />
        </div>
        <div
            v-if="showStateIconMessage"
            class="column items-center self-center"
            style="position: absolute; top: 45%"
        >
            <IconMessageItem
                :icon="
                    currentTranscript.currentState === TranscriptionState.queued
                        ? 'schedule'
                        : isCurrentTranscriptProcessing
                        ? 'settings'
                        : 'block'
                "
                :rotating="
                    currentTranscript.currentState ===
                        TranscriptionState.in_progress &&
                    isCurrentTranscriptProcessing
                "
            >
                {{
                    currentTranscript.currentState === TranscriptionState.queued
                        ? 'В очереди на обработку.'
                        : isCurrentTranscriptProcessing
                        ? 'В обработке.'
                        : 'Обработка отменена.'
                }}
                <br />
                {{
                    isCurrentTranscriptCancelling
                        ? 'Текущий фрагмент будет обработан.'
                        : ''
                }}
            </IconMessageItem>
        </div>
        <div
            class="column float-right self-end"
            :style="`top: ${
                isCurrentTranscriptProcessing
                    ? 170
                    : transcriptStore.isCancelling
                    ? 171
                    : 134
            }px; width: 56px; position: sticky`"
        >
            <div class="q-py-md" flat square style="width: 56px">
                {{
                    (
                        ((currentTranscript.chunksDurationArray?.length
                            ? currentTranscript.chunksDurationArray[
                                  currentTranscript.chunksDurationArray.length -
                                      1
                              ] > currentTranscript.audioLenSecs
                                ? currentTranscript.audioLenSecs
                                : currentTranscript.chunksDurationArray[
                                      currentTranscript.chunksDurationArray
                                          .length - 1
                                  ]
                            : 0) /
                            currentTranscript.audioLenSecs) *
                        100
                    ).toFixed(1)
                }}%
            </div>
            <q-separator inset />
            <q-btn
                class="q-pa-md"
                flat
                square
                color="primary"
                icon="close"
                title="Закрыть транскрипцию"
                @click="router.push('/transcripts')"
            />
            <q-separator inset />
            <q-btn
                :disable="
                    !currentTranscript?.chunks.length ||
                    !currentTranscript.chunks.find((chunk) => chunk.text)
                "
                class="q-pa-md"
                flat
                square
                color="primary"
                title="Экспорт в .doc"
                @click="downloadFile('doc')"
            >
                <svg
                    class="ui-export-btn"
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill-rule="evenodd"
                        d="M14 4.5V14a2 2 0 0 1-2 2v-1a1 1 0 0 0 1-1V4.5h-2A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v9H2V2a2 2 0 0 1 2-2h5.5zm-7.839 9.166v.522q0 .384-.117.641a.86.86 0 0 1-.322.387.9.9 0 0 1-.469.126.9.9 0 0 1-.471-.126.87.87 0 0 1-.32-.386 1.55 1.55 0 0 1-.117-.642v-.522q0-.386.117-.641a.87.87 0 0 1 .32-.387.87.87 0 0 1 .471-.129q.264 0 .469.13a.86.86 0 0 1 .322.386q.117.255.117.641m.803.519v-.513q0-.565-.205-.972a1.46 1.46 0 0 0-.589-.63q-.381-.22-.917-.22-.533 0-.92.22a1.44 1.44 0 0 0-.589.627q-.204.406-.205.975v.513q0 .563.205.973.205.406.59.627.386.216.92.216.535 0 .916-.216.383-.22.59-.627.204-.41.204-.973M0 11.926v4h1.459q.603 0 .999-.238a1.45 1.45 0 0 0 .595-.689q.196-.45.196-1.084 0-.63-.196-1.075a1.43 1.43 0 0 0-.59-.68q-.395-.234-1.004-.234zm.791.645h.563q.371 0 .609.152a.9.9 0 0 1 .354.454q.118.302.118.753a2.3 2.3 0 0 1-.068.592 1.1 1.1 0 0 1-.196.422.8.8 0 0 1-.334.252 1.3 1.3 0 0 1-.483.082H.79V12.57Zm7.422.483a1.7 1.7 0 0 0-.103.633v.495q0 .369.103.627a.83.83 0 0 0 .298.393.85.85 0 0 0 .478.131.9.9 0 0 0 .401-.088.7.7 0 0 0 .273-.248.8.8 0 0 0 .117-.364h.765v.076a1.27 1.27 0 0 1-.226.674q-.205.29-.55.454a1.8 1.8 0 0 1-.786.164q-.54 0-.914-.216a1.4 1.4 0 0 1-.571-.627q-.194-.408-.194-.976v-.498q0-.568.197-.978.195-.411.571-.633.378-.223.911-.223.328 0 .607.097.28.093.489.272a1.33 1.33 0 0 1 .466.964v.073H9.78a.85.85 0 0 0-.12-.38.7.7 0 0 0-.273-.261.8.8 0 0 0-.398-.097.8.8 0 0 0-.475.138.87.87 0 0 0-.301.398"
                    />
                </svg>
            </q-btn>
            <q-separator inset />
            <q-btn
                :disable="
                    !currentTranscript?.chunks.length ||
                    !currentTranscript.chunks.find((chunk) => chunk.text)
                "
                class="q-pa-md"
                flat
                square
                color="primary"
                title="Экспорт в .txt"
                @click="downloadFile('plain')"
            >
                <svg
                    class="ui-export-btn"
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill-rule="evenodd"
                        d="M14 4.5V14a2 2 0 0 1-2 2h-2v-1h2a1 1 0 0 0 1-1V4.5h-2A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v9H2V2a2 2 0 0 1 2-2h5.5zM1.928 15.849v-3.337h1.136v-.662H0v.662h1.134v3.337zm4.689-3.999h-.894L4.9 13.289h-.035l-.832-1.439h-.932l1.228 1.983-1.24 2.016h.862l.853-1.415h.035l.85 1.415h.907l-1.253-1.992zm1.93.662v3.337h-.794v-3.337H6.619v-.662h3.064v.662H8.546Z"
                    />
                </svg>
            </q-btn>
        </div>

        <div
            v-for="(timeStampView, idx) of currentTranscript.timeStampViews"
            :key="idx"
            class="q-pt-xl q-pl-xl"
            style="padding-right: 60px"
        >
            <div v-if="currentTranscript.chunks[idx].text">
                <div
                    class="ui-transcript-page-text-timestamp text-h5"
                    :id="`chunk-${idx + 1}`"
                    @click="handleAnchorClick(idx)"
                >
                    {{ timeStampView }}
                </div>
                <p class="q-mb-lg">
                    {{ currentTranscript.chunks[idx].text }}
                </p>
                <q-separator />
            </div>
        </div>
    </div>
    <q-page v-else class="fit column items-center justify-center">
        <IconMessageItem icon="warning">
            Транскрипция не найдена
        </IconMessageItem>
    </q-page>
</template>

<script setup lang="ts">
import {
    ref,
    useTemplateRef,
    onMounted,
    onUpdated,
    watch,
    computed,
} from 'vue';
import { useQuasar, copyToClipboard } from 'quasar';
import { useRoute, useRouter } from 'vue-router';
import { useTranscriptStore } from 'src/stores/transcriptStore';
import { TranscriptionState } from 'src/models/transcripts';
import IconMessageItem from 'src/components/IconMessageItem.vue';
const $q = useQuasar();
const route = useRoute();
const router = useRouter();
const transcriptStore = useTranscriptStore();

const markWidth = 6;
const markHeight = 20;
const progressBarRightPadding = 96;

await transcriptStore.loadTranscriptChunks(+route.params.taskId);
const currentTranscript = ref(
    transcriptStore.transcriptsMap.get(+route.params.taskId) || null
);

const progressMarksSvg = useTemplateRef<SVGSVGElement>('marks');
const relativeMarkPositions = ref(currentTranscript.value?.markXPositions);

const handleMarkClick = (idx: number) => {
    if (currentTranscript.value?.chunks[idx].text) {
        router.push({ name: 'transcriptPage', hash: `#chunk-${idx + 1}` });
    }
};
const handleAnchorClick = async (idx: number) => {
    handleMarkClick(idx);
    await copyToClipboard(location.href);
    $q.notify({
        position: 'top',
        message: 'Ссылка на фрагмент скопирована.',
        actions: [{ icon: 'close', color: 'white', round: true }],
    });
};

setTimeout(() => {
    if (route.hash.startsWith('#chunk-')) {
        handleMarkClick(+route.hash.slice(-1) - 1);
    }
});

const updateMarkPositions = () => {
    if (currentTranscript.value) {
        const newRelativeXes = currentTranscript.value.markXPositions.map(
            (xPos) =>
                (xPos =
                    xPos *
                        ((progressMarksSvg.value?.getBoundingClientRect()
                            .width || 0) -
                            progressBarRightPadding) -
                    markWidth)
        );
        if (newRelativeXes?.length) {
            newRelativeXes[0] += markWidth;
            relativeMarkPositions.value = newRelativeXes;
        }
    }
};
const updateTimeStampViews = () => {
    if (currentTranscript.value) {
        for (
            let i = 0;
            i < currentTranscript.value.markXPositions.length;
            i++
        ) {
            const mark = document.querySelector(`rect[rect-idx="${i}"]`);
            if (mark) {
                const timestampSpan = document.querySelector(
                    `span[span-idx="${i}"]`
                ) as HTMLSpanElement;

                timestampSpan.style.left = '';

                const xDifference =
                    mark.getBoundingClientRect().x -
                    timestampSpan.getBoundingClientRect().x;

                timestampSpan.style.left = `${
                    (xDifference < 0 ? -1 : 1) * xDifference -
                    (+timestampSpan.getBoundingClientRect().width - markWidth) /
                        2
                }px`;
            }
        }
    }
};

const downloadFile = (format: 'doc' | 'plain') => {
    if (currentTranscript.value?.chunks.length) {
        const text = currentTranscript.value.chunks
            .map(
                (chunk, chunkIdx) =>
                    `${currentTranscript.value?.timeStampViews[chunkIdx]}\n${chunk.text}`
            )
            .join('\n\n');

        if (text) {
            const element = document.createElement('a');
            element.setAttribute(
                'href',
                `data:text/${format};charset=utf-8,${encodeURIComponent(text)}`
            );
            element.setAttribute(
                'download',
                `Транскрипция №${currentTranscript.value.id}${
                    format === 'plain' ? '.txt' : `.${format}`
                }`
            );
            element.click();
            element.remove();
        }
    }
};

const cancelledWhileProcessing = ref(
    localStorage.getItem('cancelledWhileProcessing')
);

const isCurrentTranscriptProcessing = computed(
    () =>
        transcriptStore.isTranscriptProcessing(+route.params.taskId) &&
        cancelledWhileProcessing.value !== route.params.taskId
);
const isCurrentTranscriptCancelling = computed(
    () =>
        transcriptStore.isTranscriptCancelling(+route.params.taskId) ||
        cancelledWhileProcessing.value === route.params.taskId
);
const showStateIconMessage = computed(
    () =>
        currentTranscript.value &&
        [
            TranscriptionState.in_progress,
            TranscriptionState.queued,
            TranscriptionState.cancelled,
        ].includes(currentTranscript.value.currentState) &&
        !currentTranscript.value.chunks.length
);

const resizeObserver = new ResizeObserver(() => updateMarkPositions());
onMounted(() => {
    if (progressMarksSvg.value) {
        resizeObserver.observe(progressMarksSvg.value);
    }
});
onUpdated(() => {
    updateTimeStampViews();
});
watch(
    () => route.params.taskId,
    async (newId) => {
        await transcriptStore.loadTranscriptChunks(+route.params.taskId);

        const anotherTranscript = transcriptStore.transcriptsMap.get(+newId);
        if (anotherTranscript) {
            if (
                ![
                    TranscriptionState.queued,
                    TranscriptionState.in_progress,
                    TranscriptionState.processing_error,
                ].includes(anotherTranscript.currentState)
            ) {
            }
            currentTranscript.value = anotherTranscript;
            relativeMarkPositions.value = anotherTranscript.markXPositions;
            updateMarkPositions();
        } else {
            currentTranscript.value = null;
        }
    }
);
watch(
    () => transcriptStore.processsingTicks,
    () => {
        if (
            transcriptStore.processingTranscriptionId &&
            +route.params.taskId === transcriptStore.processingTranscriptionId
        ) {
            cancelledWhileProcessing.value = localStorage.getItem(
                'cancelledWhileProcessing'
            );
            currentTranscript.value = transcriptStore.processingTranscription!;
            relativeMarkPositions.value =
                transcriptStore.processingTranscription!.markXPositions;
            updateMarkPositions();
        }
    }
);
</script>

<style scoped lang="scss">
.ui-transcript-page-progress-container {
    position: sticky;
    top: 50px;
    background-color: white;
}
.ui-trancscript-page-progress-bar {
    position: relative;
    overflow-x: hidden;
}
.ui-trancscript-page-progress-bar-marks {
    position: absolute;
    rect {
        cursor: pointer;
        &.ui-progress-mark {
            &-processing {
                fill: $warning;
            }
            &-complete {
                fill: $primary;
            }
            &-empty {
                fill: lightgray;
                cursor: default;
            }
        }
    }
}
.ui-transcript-page-progress-timestamp {
    position: relative;
    cursor: pointer;
    &.empty {
        color: lightgray;
        cursor: default;
    }
}
.ui-transcript-page-text-timestamp {
    cursor: pointer;
    &:hover::after {
        content: ' #';
    }
}
.ui-export-btn {
    fill: $primary;
}
</style>
