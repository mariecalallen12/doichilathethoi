<template>
  <div class="relative">
    <button
      @click="showPicker = !showPicker"
      class="flex items-center space-x-2 px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white hover:border-purple-500/50 transition-all"
    >
      <i class="fas fa-calendar-alt text-purple-400"></i>
      <span>{{ displayText }}</span>
      <i class="fas fa-chevron-down text-xs"></i>
    </button>

    <div
      v-if="showPicker"
      class="absolute top-full left-0 mt-2 glass-panel rounded-lg p-4 z-50 min-w-[300px]"
    >
      <!-- Quick Presets -->
      <div class="mb-4">
        <div class="text-purple-300 text-xs mb-2">Chọn nhanh</div>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="preset in presets"
            :key="preset.label"
            @click="selectPreset(preset)"
            class="px-3 py-2 text-sm text-white hover:bg-purple-500/20 rounded transition-colors"
          >
            {{ preset.label }}
          </button>
        </div>
      </div>

      <!-- Custom Range -->
      <div class="space-y-3">
        <div>
          <label class="text-purple-300 text-xs mb-1 block">Từ ngày</label>
          <input
            v-model="startDate"
            type="date"
            class="w-full px-3 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          />
        </div>
        <div>
          <label class="text-purple-300 text-xs mb-1 block">Đến ngày</label>
          <input
            v-model="endDate"
            type="date"
            class="w-full px-3 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
          />
        </div>
        <div class="flex space-x-2">
          <button
            @click="applyCustomRange"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg hover:from-purple-600 hover:to-indigo-600 transition-all"
          >
            Áp dụng
          </button>
          <button
            @click="reset"
            class="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-all"
          >
            Đặt lại
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ start: null, end: null }),
  },
});

const emit = defineEmits(['update:modelValue']);

const showPicker = ref(false);
const startDate = ref('');
const endDate = ref('');

const presets = [
  { label: 'Hôm nay', days: 0 },
  { label: 'Hôm qua', days: 1 },
  { label: '7 ngày qua', days: 7 },
  { label: '30 ngày qua', days: 30 },
  { label: 'Tháng này', days: null, type: 'thisMonth' },
  { label: 'Tháng trước', days: null, type: 'lastMonth' },
];

const displayText = computed(() => {
  if (props.modelValue.start && props.modelValue.end) {
    const start = new Date(props.modelValue.start).toLocaleDateString('vi-VN');
    const end = new Date(props.modelValue.end).toLocaleDateString('vi-VN');
    return `${start} - ${end}`;
  }
  return 'Chọn khoảng thời gian';
});

const selectPreset = (preset) => {
  const today = new Date();
  let start, end;

  if (preset.type === 'thisMonth') {
    start = new Date(today.getFullYear(), today.getMonth(), 1);
    end = today;
  } else if (preset.type === 'lastMonth') {
    start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    end = new Date(today.getFullYear(), today.getMonth(), 0);
  } else {
    end = new Date(today);
    end.setHours(23, 59, 59, 999);
    start = new Date(today);
    start.setDate(start.getDate() - preset.days);
    start.setHours(0, 0, 0, 0);
  }

  emit('update:modelValue', {
    start: start.toISOString(),
    end: end.toISOString(),
  });

  startDate.value = start.toISOString().split('T')[0];
  endDate.value = end.toISOString().split('T')[0];
  showPicker.value = false;
};

const applyCustomRange = () => {
  if (startDate.value && endDate.value) {
    emit('update:modelValue', {
      start: new Date(startDate.value).toISOString(),
      end: new Date(endDate.value).toISOString(),
    });
    showPicker.value = false;
  }
};

const reset = () => {
  startDate.value = '';
  endDate.value = '';
  emit('update:modelValue', { start: null, end: null });
};

const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showPicker.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  if (props.modelValue.start) {
    startDate.value = new Date(props.modelValue.start).toISOString().split('T')[0];
  }
  if (props.modelValue.end) {
    endDate.value = new Date(props.modelValue.end).toISOString().split('T')[0];
  }
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

