<template>
  <div class="animate-pulse">
    <div v-if="type === 'card'" class="glass-panel rounded-lg p-4">
      <div class="h-4 bg-purple-500/20 rounded w-3/4 mb-4"></div>
      <div class="h-8 bg-purple-500/20 rounded w-1/2 mb-2"></div>
      <div class="h-4 bg-purple-500/20 rounded w-full"></div>
    </div>
    <div v-else-if="type === 'table'" class="space-y-3">
      <div v-for="i in rows" :key="i" class="flex space-x-4">
        <div v-for="j in columns" :key="j" class="h-4 bg-purple-500/20 rounded flex-1"></div>
      </div>
    </div>
    <div v-else-if="type === 'text'" class="space-y-2">
      <div class="h-4 bg-purple-500/20 rounded" :style="{ width: width }"></div>
    </div>
    <div v-else class="h-4 bg-purple-500/20 rounded" :style="{ width: width }"></div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['card', 'table', 'text'].includes(value),
  },
  width: {
    type: String,
    default: '100%',
  },
  rows: {
    type: Number,
    default: 3,
  },
  columns: {
    type: Number,
    default: 4,
  },
});
</script>

