<template>
    <Suspense>
        <router-view />
    </Suspense>
</template>

<script setup lang="ts">
defineOptions({
    name: 'App',
});
</script>
