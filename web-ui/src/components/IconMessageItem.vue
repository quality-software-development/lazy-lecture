<template>
    <q-icon
        :class="rotating ? 'ui-icon-rotating' : ''"
        size="100px"
        :name="icon"
        color="grey-5"
    />
    <p class="text-h6 text-grey-5 text-center"><slot></slot></p>
</template>

<script setup lang="ts">
defineProps<{
    icon: string;
    rotating?: boolean;
}>();
</script>

<style scoped>
@keyframes rotating {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
.ui-icon-rotating {
    animation: rotating 3s linear infinite;
}
</style>
