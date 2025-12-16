<template>
  <div class="indicator-library">
    <div class="mb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Tìm kiếm chỉ báo..."
        class="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white text-sm placeholder-gray-400"
      />
    </div>

    <div class="space-y-2 max-h-96 overflow-y-auto">
      <div
        v-for="indicator in filteredIndicators"
        :key="indicator.id"
        class="p-3 bg-slate-700/50 hover:bg-slate-700 rounded cursor-pointer transition-all"
        @click="selectIndicator(indicator)"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm font-semibold text-white">{{ indicator.name }}</div>
            <div class="text-xs text-gray-400">{{ indicator.description }}</div>
          </div>
          <i class="fas fa-plus text-purple-400"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const emit = defineEmits(['indicator-selected']);

const searchQuery = ref('');

const indicators = [
  { id: 'rsi', name: 'RSI', description: 'Relative Strength Index', category: 'momentum' },
  { id: 'macd', name: 'MACD', description: 'Moving Average Convergence Divergence', category: 'trend' },
  { id: 'bollinger', name: 'Bollinger Bands', description: 'Bollinger Bands', category: 'volatility' },
  { id: 'sma', name: 'SMA', description: 'Simple Moving Average', category: 'trend' },
  { id: 'ema', name: 'EMA', description: 'Exponential Moving Average', category: 'trend' },
  { id: 'stochastic', name: 'Stochastic', description: 'Stochastic Oscillator', category: 'momentum' },
  { id: 'adx', name: 'ADX', description: 'Average Directional Index', category: 'trend' },
  { id: 'atr', name: 'ATR', description: 'Average True Range', category: 'volatility' },
  { id: 'fibonacci', name: 'Fibonacci', description: 'Fibonacci Retracement', category: 'drawing' },
  { id: 'trendline', name: 'Trend Line', description: 'Trend Line', category: 'drawing' },
];

const filteredIndicators = computed(() => {
  if (!searchQuery.value) return indicators;
  const query = searchQuery.value.toLowerCase();
  return indicators.filter(i => 
    i.name.toLowerCase().includes(query) ||
    i.description.toLowerCase().includes(query)
  );
});

const selectIndicator = (indicator) => {
  emit('indicator-selected', indicator);
};
</script>

<style scoped>
.indicator-library {
  max-height: 400px;
}
</style>

