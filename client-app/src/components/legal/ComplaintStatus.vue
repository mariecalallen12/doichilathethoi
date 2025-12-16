<template>
  <div
    v-if="complaint"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm overflow-y-auto"
    @click.self="close"
  >
    <div class="relative w-full max-w-3xl mx-4 my-8 bg-slate-900 rounded-xl overflow-hidden border border-purple-500/20">
      <!-- Close Button -->
      <button
        @click="close"
        class="absolute top-4 right-4 z-10 w-10 h-10 bg-black/70 hover:bg-black/90 rounded-full flex items-center justify-center text-white transition-all"
      >
        <i class="fas fa-times"></i>
      </button>

      <!-- Content -->
      <div class="p-8">
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-white">{{ complaint.title }}</h2>
            <span
              class="px-3 py-1 rounded text-sm font-semibold"
              :class="getStatusClass(complaint.status)"
            >
              {{ getStatusLabel(complaint.status) }}
            </span>
          </div>
          <div class="text-sm text-gray-400">
            <span>Mã khiếu nại: <span class="text-white font-mono">{{ complaint.id }}</span></span>
            <span class="ml-4">Ngày tạo: {{ formatDate(complaint.created_at) }}</span>
          </div>
        </div>

        <!-- Description -->
        <div class="mb-6">
          <h3 class="text-lg font-bold text-white mb-2">Mô tả</h3>
          <p class="text-gray-300">{{ complaint.description }}</p>
        </div>

        <!-- Status Timeline -->
        <div class="mb-6">
          <h3 class="text-lg font-bold text-white mb-4">Lịch Sử Xử Lý</h3>
          <div class="space-y-4">
            <div
              v-for="(update, index) in complaint.updates || []"
              :key="index"
              class="flex items-start space-x-4"
            >
              <div class="flex flex-col items-center">
                <div class="w-3 h-3 bg-purple-400 rounded-full"></div>
                <div v-if="index < (complaint.updates?.length || 1) - 1" class="w-0.5 h-full bg-purple-400/30 mt-2"></div>
              </div>
              <div class="flex-1">
                <div class="text-white font-semibold">{{ update.status }}</div>
                <div class="text-sm text-gray-400">{{ update.message }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ formatDate(update.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Attachments -->
        <div v-if="complaint.attachments && complaint.attachments.length > 0" class="mb-6">
          <h3 class="text-lg font-bold text-white mb-4">Tài Liệu Đính Kèm</h3>
          <div class="space-y-2">
            <a
              v-for="attachment in complaint.attachments"
              :key="attachment.id"
              :href="attachment.url"
              target="_blank"
              class="flex items-center space-x-2 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-all"
            >
              <i class="fas fa-file text-purple-400"></i>
              <span class="text-white">{{ attachment.name }}</span>
              <i class="fas fa-external-link-alt text-gray-400 ml-auto"></i>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  complaint: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-500/20 text-yellow-400',
    in_progress: 'bg-blue-500/20 text-blue-400',
    resolved: 'bg-green-500/20 text-green-400',
    closed: 'bg-gray-500/20 text-gray-400'
  };
  return classes[status] || 'bg-gray-500/20 text-gray-400';
};

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Chờ xử lý',
    in_progress: 'Đang xử lý',
    resolved: 'Đã giải quyết',
    closed: 'Đã đóng'
  };
  return labels[status] || status;
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
</script>

<style scoped>
/* Complaint status styles */
</style>

