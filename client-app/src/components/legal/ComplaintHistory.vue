<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
    <h3 class="text-xl font-bold text-white mb-4">Lịch Sử Khiếu Nại</h3>
    
    <div v-if="complaints.length === 0" class="text-center py-8 text-gray-400">
      <i class="fas fa-inbox text-4xl mb-4"></i>
      <p>Chưa có khiếu nại nào</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="complaint in complaints"
        :key="complaint.id"
        class="p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-all cursor-pointer"
        @click="$emit('view-detail', complaint.id)"
      >
        <div class="flex items-start justify-between mb-2">
          <h4 class="text-white font-semibold line-clamp-1">{{ complaint.title }}</h4>
          <span
            class="px-2 py-1 rounded text-xs font-semibold ml-2 whitespace-nowrap"
            :class="getStatusClass(complaint.status)"
          >
            {{ getStatusLabel(complaint.status) }}
          </span>
        </div>
        <p class="text-sm text-gray-400 mb-2 line-clamp-2">{{ complaint.description }}</p>
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>{{ formatDate(complaint.created_at) }}</span>
          <span class="text-purple-400">Xem chi tiết <i class="fas fa-chevron-right"></i></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  complaints: {
    type: Array,
    default: () => []
  }
});

defineEmits(['view-detail']);

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
    month: 'short',
    day: 'numeric'
  });
};
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

