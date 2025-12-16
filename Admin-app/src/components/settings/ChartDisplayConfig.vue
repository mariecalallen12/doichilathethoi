<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../../services/api';
import toastService from '../../services/toast';
import Card from '../ui/Card.vue';
import Button from '../ui/Button.vue';
import Select from '../ui/Select.vue';
import Input from '../ui/Input.vue';

const props = defineProps({
  // Optional: pre-loaded config
  initialConfig: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['configUpdated']);

const loading = ref(false);
const config = ref({
  upColor: '#10B981',      // Green for up candles
  downColor: '#EF4444',    // Red for down candles
  wickUpColor: '#10B981',  // Wick color for up candles
  wickDownColor: '#EF4444', // Wick color for down candles
  borderVisible: false,
  shadowStyle: 'normal',   // normal, short, long
  backgroundColor: '#1e293b',
  gridColor: '#334155',
  textColor: '#e2e8f0',
});

const shadowStyleOptions = [
  { label: 'Bình thường', value: 'normal' },
  { label: 'Ngắn (Short)', value: 'short' },
  { label: 'Dài (Long)', value: 'long' },
  { label: 'Dotted', value: 'dotted' },
];

const presetThemes = [
  {
    name: 'Default (Dark)',
    config: {
      upColor: '#10B981',
      downColor: '#EF4444',
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444',
      backgroundColor: '#1e293b',
      gridColor: '#334155',
      textColor: '#e2e8f0',
    },
  },
  {
    name: 'Classic (Green/Red)',
    config: {
      upColor: '#26A69A',
      downColor: '#EF5350',
      wickUpColor: '#26A69A',
      wickDownColor: '#EF5350',
      backgroundColor: '#131722',
      gridColor: '#2a2e39',
      textColor: '#d1d4dc',
    },
  },
  {
    name: 'Blue Theme',
    config: {
      upColor: '#2196F3',
      downColor: '#FF5722',
      wickUpColor: '#2196F3',
      wickDownColor: '#FF5722',
      backgroundColor: '#0d1117',
      gridColor: '#21262d',
      textColor: '#c9d1d9',
    },
  },
  {
    name: 'Neon',
    config: {
      upColor: '#00FF88',
      downColor: '#FF0055',
      wickUpColor: '#00FF88',
      wickDownColor: '#FF0055',
      backgroundColor: '#0a0a0a',
      gridColor: '#1a1a2e',
      textColor: '#eaeaea',
    },
  },
];

const applyPreset = (preset) => {
  config.value = { ...config.value, ...preset.config };
  toastService.info(`Đã áp dụng theme: ${preset.name}`);
};

const fetchConfig = async () => {
  if (props.initialConfig) {
    config.value = { ...config.value, ...props.initialConfig };
    return;
  }

  loading.value = true;
  try {
    const res = await api.get('/api/admin/settings/chart-display');
    if (res.data?.data) {
      config.value = { ...config.value, ...res.data.data };
    }
  } catch (error) {
    console.warn('Could not fetch chart display config:', error);
    // Use default config
  } finally {
    loading.value = false;
  }
};

const saveConfig = async () => {
  loading.value = true;
  try {
    await api.patch('/api/admin/config/candle', config.value);
    toastService.success('Đã lưu cấu hình hiển thị chart');
    emit('configUpdated', config.value);
  } catch (error) {
    console.error('Save chart config error:', error);
    toastService.error(error?.response?.data?.detail || 'Không thể lưu cấu hình');
  } finally {
    loading.value = false;
  }
};

const resetToDefault = () => {
  config.value = {
    upColor: '#10B981',
    downColor: '#EF4444',
    wickUpColor: '#10B981',
    wickDownColor: '#EF4444',
    borderVisible: false,
    shadowStyle: 'normal',
    backgroundColor: '#1e293b',
    gridColor: '#334155',
    textColor: '#e2e8f0',
  };
  toastService.info('Đã khôi phục cấu hình mặc định');
};

onMounted(() => {
  fetchConfig();
});
</script>

<template>
  <Card title="Cấu hình hiển thị Chart">
    <div class="space-y-6">
      <!-- Preset Themes -->
      <div>
        <label class="block text-sm text-white/80 mb-2">Theme có sẵn</label>
        <div class="flex flex-wrap gap-2">
          <Button
            v-for="preset in presetThemes"
            :key="preset.name"
            variant="outline"
            size="sm"
            @click="applyPreset(preset)"
          >
            <span
              class="w-3 h-3 rounded-full mr-2"
              :style="{ backgroundColor: preset.config.upColor }"
            ></span>
            {{ preset.name }}
          </Button>
        </div>
      </div>

      <!-- Color Pickers -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-white/80 mb-1.5">Màu nến tăng (Up)</label>
          <div class="flex items-center gap-2">
            <input
              type="color"
              v-model="config.upColor"
              class="w-12 h-10 rounded border border-white/10 bg-transparent cursor-pointer"
            />
            <Input v-model="config.upColor" placeholder="#10B981" class="flex-1" />
          </div>
        </div>

        <div>
          <label class="block text-sm text-white/80 mb-1.5">Màu nến giảm (Down)</label>
          <div class="flex items-center gap-2">
            <input
              type="color"
              v-model="config.downColor"
              class="w-12 h-10 rounded border border-white/10 bg-transparent cursor-pointer"
            />
            <Input v-model="config.downColor" placeholder="#EF4444" class="flex-1" />
          </div>
        </div>

        <div>
          <label class="block text-sm text-white/80 mb-1.5">Màu bấc nến tăng (Wick Up)</label>
          <div class="flex items-center gap-2">
            <input
              type="color"
              v-model="config.wickUpColor"
              class="w-12 h-10 rounded border border-white/10 bg-transparent cursor-pointer"
            />
            <Input v-model="config.wickUpColor" placeholder="#10B981" class="flex-1" />
          </div>
        </div>

        <div>
          <label class="block text-sm text-white/80 mb-1.5">Màu bấc nến giảm (Wick Down)</label>
          <div class="flex items-center gap-2">
            <input
              type="color"
              v-model="config.wickDownColor"
              class="w-12 h-10 rounded border border-white/10 bg-transparent cursor-pointer"
            />
            <Input v-model="config.wickDownColor" placeholder="#EF4444" class="flex-1" />
          </div>
        </div>

        <div>
          <label class="block text-sm text-white/80 mb-1.5">Màu nền chart</label>
          <div class="flex items-center gap-2">
            <input
              type="color"
              v-model="config.backgroundColor"
              class="w-12 h-10 rounded border border-white/10 bg-transparent cursor-pointer"
            />
            <Input v-model="config.backgroundColor" placeholder="#1e293b" class="flex-1" />
          </div>
        </div>

        <div>
          <label class="block text-sm text-white/80 mb-1.5">Màu lưới (Grid)</label>
          <div class="flex items-center gap-2">
            <input
              type="color"
              v-model="config.gridColor"
              class="w-12 h-10 rounded border border-white/10 bg-transparent cursor-pointer"
            />
            <Input v-model="config.gridColor" placeholder="#334155" class="flex-1" />
          </div>
        </div>
      </div>

      <!-- Shadow Style -->
      <div>
        <Select
          v-model="config.shadowStyle"
          :options="shadowStyleOptions"
          label="Kiểu bấc nến (Shadow Style)"
          placeholder="Chọn kiểu bấc nến"
        />
        <p class="text-xs text-white/50 mt-1">
          Bình thường = tỷ lệ thực, Ngắn = bấc ngắn hơn, Dài = bấc dài hơn, Dotted = bấc chấm chấm
        </p>
      </div>

      <!-- Preview Box -->
      <div class="p-4 rounded-lg border border-white/10" :style="{ backgroundColor: config.backgroundColor }">
        <p class="text-sm mb-3" :style="{ color: config.textColor }">Preview:</p>
        <div class="flex items-end justify-center gap-4 h-24">
          <!-- Up Candle -->
          <div class="flex flex-col items-center">
            <div 
              class="w-0.5 h-4"
              :style="{ backgroundColor: config.wickUpColor }"
            ></div>
            <div 
              class="w-6 h-12 rounded-sm"
              :style="{ backgroundColor: config.upColor }"
            ></div>
            <div 
              class="w-0.5 h-2"
              :style="{ backgroundColor: config.wickUpColor }"
            ></div>
            <span class="text-xs mt-1" :style="{ color: config.textColor }">Tăng</span>
          </div>
          <!-- Down Candle -->
          <div class="flex flex-col items-center">
            <div 
              class="w-0.5 h-2"
              :style="{ backgroundColor: config.wickDownColor }"
            ></div>
            <div 
              class="w-6 h-8 rounded-sm"
              :style="{ backgroundColor: config.downColor }"
            ></div>
            <div 
              class="w-0.5 h-4"
              :style="{ backgroundColor: config.wickDownColor }"
            ></div>
            <span class="text-xs mt-1" :style="{ color: config.textColor }">Giảm</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-between pt-4 border-t border-white/10">
        <Button variant="outline" @click="resetToDefault">
          <i class="fas fa-undo mr-2"></i>
          Khôi phục mặc định
        </Button>
        <Button variant="primary" :loading="loading" @click="saveConfig">
          <i class="fas fa-save mr-2"></i>
          Lưu cấu hình
        </Button>
      </div>
    </div>
  </Card>
</template>
