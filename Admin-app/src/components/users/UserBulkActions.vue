<script setup>
import Button from '../ui/Button.vue';

const props = defineProps({
  selectedCount: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits(['bulk-activate', 'bulk-suspend', 'bulk-ban', 'clear-selection']);
</script>

<template>
  <div
    v-if="selectedCount > 0"
    class="glass-effect rounded-xl p-4 mb-4 flex items-center justify-between"
  >
    <div class="flex items-center gap-3">
      <span class="text-white font-medium">{{ selectedCount }} người dùng đã chọn</span>
    </div>
    <div class="flex items-center gap-2">
      <Button variant="secondary" size="sm" @click="emit('bulk-activate')">
        <i class="fas fa-check mr-2"></i>
        Kích hoạt
      </Button>
      <Button variant="warning" size="sm" @click="emit('bulk-suspend')">
        <i class="fas fa-pause mr-2"></i>
        Tạm khóa
      </Button>
      <Button variant="danger" size="sm" @click="emit('bulk-ban')">
        <i class="fas fa-ban mr-2"></i>
        Cấm
      </Button>
      <Button variant="ghost" size="sm" @click="emit('clear-selection')">
        <i class="fas fa-times mr-2"></i>
        Bỏ chọn
      </Button>
    </div>
  </div>
</template>

<style scoped>
.glass-effect {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

