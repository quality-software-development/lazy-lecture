<template>
    <q-icon size="100px" :name="icon" color="grey-5" />
    <p class="text-h6 text-grey-5 text-center"><slot></slot></p>
</template>

<script setup lang="ts">
defineProps<{
    icon: string;
}>();
</script>
