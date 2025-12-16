<template>
  <span
    :class="[
      'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
      statusClasses[status] || statusClasses.default
    ]"
  >
    <i :class="[iconClasses[status] || iconClasses.default, 'mr-1']"></i>
    {{ statusText }}
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['completed', 'pending', 'processing', 'failed', 'cancelled', 'rejected'].includes(value),
  },
});

const statusTextMap = {
  completed: 'Hoàn thành',
  pending: 'Chờ xử lý',
  processing: 'Đang xử lý',
  failed: 'Thất bại',
  cancelled: 'Đã hủy',
  rejected: 'Bị từ chối',
};

const statusClasses = {
  completed: 'bg-green-500/20 text-green-400 border border-green-500/30',
  pending: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
  processing: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
  failed: 'bg-red-500/20 text-red-400 border border-red-500/30',
  cancelled: 'bg-gray-500/20 text-gray-400 border border-gray-500/30',
  rejected: 'bg-red-500/20 text-red-400 border border-red-500/30',
  default: 'bg-gray-500/20 text-gray-400 border border-gray-500/30',
};

const iconClasses = {
  completed: 'fas fa-check-circle',
  pending: 'fas fa-clock',
  processing: 'fas fa-spinner fa-spin',
  failed: 'fas fa-times-circle',
  cancelled: 'fas fa-ban',
  rejected: 'fas fa-times-circle',
  default: 'fas fa-question-circle',
};

const statusText = computed(() => {
  return statusTextMap[props.status] || props.status;
});
</script>

