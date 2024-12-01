<template>
    <div v-if="currentTranscript">
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
                    :value="
                        currentTranscript.chunksDurationArray[
                            currentTranscript.chunksDurationArray.length - 1
                        ] / currentTranscript.duration
                    "
                    color="primary"
                    animation-speed="100"
                />
            </div>
            <div class="row q-mb-sm">
                <span
                    class="ui-transcript-page-progress-timestamp"
                    v-for="(
                        chunkTimeStamp, idx
                    ) of currentTranscript.timeStampViews"
                    :key="idx"
                    @click="handleMarkClick(idx)"
                    :span-idx="idx"
                    >{{ chunkTimeStamp }}</span
                >
            </div>
            <q-separator />
        </div>
        <div
            v-for="(timeStampView, idx) of currentTranscript.timeStampViews"
            :key="idx"
            class="q-pa-lg q-pl-xl q-pt-xl"
        >
            <div>
                <div
                    class="ui-transcript-page-text-timestamp text-h5"
                    :id="`chunk-${idx + 1}`"
                    @click="handleAnchorClick(idx)"
                >
                    {{ timeStampView }}
                </div>
                <p>
                    {{ currentTranscript.chunks[idx].text }}
                </p>
            </div>
            <div style="height: 1000px"></div>
        </div>
    </div>
    <q-page v-else class="fit column items-center justify-center">
        <q-icon size="300px" name="warning" color="grey-5" />
        <div class="text-h4 text-grey-5">Транскрипция не найдена</div>
    </q-page>
</template>

<script setup lang="ts">
import { ref, useTemplateRef, onMounted, onUpdated, watch } from 'vue';
import { useQuasar, copyToClipboard } from 'quasar';
import { useRoute, useRouter } from 'vue-router';
import { useTranscriptStore } from 'src/stores/transcriptStore';
const $q = useQuasar();
const route = useRoute();
const router = useRouter();
const transcriptStore = useTranscriptStore();
const markWidth = 6;
const markHeight = 20;
const progressBarRightPadding = 96;

await transcriptStore.loadTranscriptChunks(+route.params.taskId, 0, 100);
const currentTranscript = ref(
    transcriptStore.transcriptsMap.get(+route.params.taskId) || null
);

const progressMarksSvg = useTemplateRef<SVGSVGElement>('marks');
const relativeMarkPositions = ref(currentTranscript.value?.markXPositions);

const handleMarkClick = (idx: number) => {
    router.push({ name: 'transcriptPage', hash: `#chunk-${idx + 1}` });
};
const handleAnchorClick = async (idx: number) => {
    handleMarkClick(idx);
    await copyToClipboard(location.href);
    $q.notify({
        position: 'top',
        message: 'Ссылка на фрагмент скопирована.',
        actions: [
            { icon: 'close', color: 'white', round: true },
        ],
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
                        (progressMarksSvg.value!.getBoundingClientRect().width -
                            progressBarRightPadding) -
                    markWidth)
        );
        if (newRelativeXes) {
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
            const markAbsoluteX = document
                .querySelector(`rect[rect-idx="${i}"]`)
                ?.getAttribute('x');
            const timestampSpan = document.querySelector(
                `span[span-idx="${i}"]`
            ) as HTMLSpanElement;
            timestampSpan.style.left = `${
                +(markAbsoluteX || 0) -
                i * +timestampSpan.getBoundingClientRect().width +
                20
            }px`;
        }
    }
};

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
        await transcriptStore.loadTranscriptChunks(
            +route.params.taskId,
            0,
            100
        );

        const anotherTranscript = transcriptStore.transcriptsMap.get(+newId);
        if (anotherTranscript) {
            if (!currentTranscript.value) {
                location.reload();
                return;
            }
            currentTranscript.value = anotherTranscript;
            relativeMarkPositions.value = anotherTranscript.markXPositions;
            updateMarkPositions();
        } else {
            currentTranscript.value = null;
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
        fill: $primary;
        cursor: pointer;
    }
}
.ui-transcript-page-progress-timestamp {
    position: relative;
    cursor: pointer;
}
.ui-transcript-page-text-timestamp {
    cursor: pointer;
    &:hover::after {
        content: ' #';
    }
}
</style>
