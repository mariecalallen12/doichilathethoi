<template>
  <div
    v-if="event"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
    @click.self="close"
  >
    <div class="relative w-full max-w-2xl mx-4 bg-slate-900 rounded-xl overflow-hidden border border-purple-500/20">
      <!-- Close Button -->
      <button
        @click="close"
        class="absolute top-4 right-4 z-10 w-10 h-10 bg-black/70 hover:bg-black/90 rounded-full flex items-center justify-center text-white transition-all"
      >
        <i class="fas fa-times"></i>
      </button>

      <!-- Content -->
      <div class="p-6">
        <!-- Header -->
        <div class="flex items-center space-x-3 mb-4">
          <span
            class="px-3 py-1 rounded text-sm font-semibold"
            :class="{
              'bg-red-500/20 text-red-400': event.importance === 'high',
              'bg-yellow-500/20 text-yellow-400': event.importance === 'medium',
              'bg-green-500/20 text-green-400': event.importance === 'low'
            }"
          >
            {{ getImportanceLabel(event.importance) }}
          </span>
          <span class="px-3 py-1 bg-purple-500/20 text-purple-400 rounded text-sm">
            {{ event.country }}
          </span>
          <span class="text-gray-400 text-sm">
            {{ formatDate(event.date) }}
          </span>
        </div>

        <h2 class="text-2xl font-bold text-white mb-4">{{ event.title }}</h2>
        <p class="text-gray-300 mb-6">{{ event.description }}</p>

        <!-- Details -->
        <div class="space-y-4">
          <div v-if="event.currency" class="flex items-center space-x-2">
            <i class="fas fa-dollar-sign text-purple-400"></i>
            <span class="text-gray-300">Tiền tệ: <span class="text-white font-semibold">{{ event.currency }}</span></span>
          </div>
          <div v-if="event.impact" class="flex items-center space-x-2">
            <i class="fas fa-chart-line text-purple-400"></i>
            <span class="text-gray-300">Tác động: <span class="text-white font-semibold">{{ getImpactLabel(event.impact) }}</span></span>
          </div>
          <div v-if="event.previous" class="flex items-center space-x-2">
            <i class="fas fa-history text-purple-400"></i>
            <span class="text-gray-300">Giá trị trước: <span class="text-white font-semibold">{{ event.previous }}</span></span>
          </div>
          <div v-if="event.forecast" class="flex items-center space-x-2">
            <i class="fas fa-crystal-ball text-purple-400"></i>
            <span class="text-gray-300">Dự báo: <span class="text-white font-semibold">{{ event.forecast }}</span></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  event: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getImportanceLabel = (importance) => {
  const labels = {
    high: 'Cao',
    medium: 'Trung bình',
    low: 'Thấp'
  };
  return labels[importance] || importance;
};

const getImpactLabel = (impact) => {
  const labels = {
    high: 'Cao',
    medium: 'Trung bình',
    low: 'Thấp'
  };
  return labels[impact] || impact;
};
</script>

<style scoped>
/* Event detail modal styles */
</style>

