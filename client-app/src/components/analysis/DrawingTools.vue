<template>
  <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20 mt-6">
    <h3 class="text-xl font-bold text-white mb-4">Công Cụ Vẽ</h3>
    
    <div class="flex flex-wrap gap-2">
      <button
        v-for="tool in tools"
        :key="tool.id"
        @click="selectTool(tool.id)"
        class="px-4 py-2 rounded-lg transition-all"
        :class="{
          'bg-purple-600 text-white': selectedTool === tool.id,
          'bg-slate-700 text-gray-300 hover:bg-slate-600': selectedTool !== tool.id
        }"
      >
        <i :class="tool.icon" class="mr-2"></i>
        {{ tool.name }}
      </button>
    </div>

    <div v-if="selectedTool" class="mt-4 text-sm text-gray-400">
      <p>Chọn công cụ: <span class="text-white font-semibold">{{ getToolName(selectedTool) }}</span></p>
      <p class="mt-2">Nhấp và kéo trên biểu đồ để vẽ</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['drawing-complete']);

const selectedTool = ref(null);

const tools = [
  { id: 'trendline', name: 'Đường Xu Hướng', icon: 'fas fa-chart-line' },
  { id: 'fibonacci', name: 'Fibonacci', icon: 'fas fa-wave-square' },
  { id: 'rectangle', name: 'Hình Chữ Nhật', icon: 'fas fa-square' },
  { id: 'ellipse', name: 'Hình Elip', icon: 'fas fa-circle' },
  { id: 'arrow', name: 'Mũi Tên', icon: 'fas fa-arrow-right' },
  { id: 'text', name: 'Văn Bản', icon: 'fas fa-font' },
];

const selectTool = (toolId) => {
  selectedTool.value = selectedTool.value === toolId ? null : toolId;
  // Emit tool selection
  if (selectedTool.value) {
    emit('drawing-complete', { tool: selectedTool.value, action: 'selected' });
  }
};

const getToolName = (toolId) => {
  const tool = tools.find(t => t.id === toolId);
  return tool ? tool.name : toolId;
};
</script>

<style scoped>
/* Drawing tools styles */
</style>

