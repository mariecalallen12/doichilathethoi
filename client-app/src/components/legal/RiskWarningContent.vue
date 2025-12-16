<template>
  <div class="prose prose-invert max-w-none text-gray-300" v-html="content"></div>
</template>

<script setup>
defineProps({
  content: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
/* Risk warning content styles */
</style>

