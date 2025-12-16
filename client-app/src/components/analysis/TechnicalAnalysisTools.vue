<template>
  <section id="technical" class="mb-12">
    <div class="mb-6">
      <h2 class="text-3xl font-bold text-white mb-2">Phân Tích Kỹ Thuật</h2>
      <p class="text-purple-200/80">Công cụ và chỉ báo kỹ thuật chuyên nghiệp</p>
    </div>

    <!-- Chart with Indicators -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Main Chart -->
      <div class="lg:col-span-2 bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="text-xl font-bold text-white">Biểu Đồ Giá</h3>
          <div class="flex items-center space-x-2">
            <select
              v-model="timeFrame"
              @change="handleTimeFrameChange"
              class="px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white text-sm"
            >
              <option value="1m">1M</option>
              <option value="5m">5M</option>
              <option value="15m">15M</option>
              <option value="1h">1H</option>
              <option value="4h">4H</option>
              <option value="1d">1D</option>
            </select>
          </div>
        </div>
        <!-- Loading State -->
        <div v-if="analysisStore.isLoading" class="flex items-center justify-center" style="height: 400px;">
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-400 mb-4"></div>
            <p class="text-purple-200">Đang tải dữ liệu...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="analysisStore.error" class="flex items-center justify-center" style="height: 400px;">
          <div class="text-center max-w-md px-4">
            <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
            <p class="text-red-400 mb-4">{{ analysisStore.error }}</p>
            <button
              @click="retryLoad"
              class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all"
            >
              <i class="fas fa-redo mr-2"></i>Thử lại
            </button>
          </div>
        </div>

        <!-- Chart Container -->
        <div v-else ref="chartContainer" class="chart-container" style="height: 400px;"></div>
      </div>

      <!-- Indicators Panel -->
      <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-500/20">
        <h3 class="text-xl font-bold text-white mb-4">Chỉ Báo Kỹ Thuật</h3>
        
        <!-- Indicator Library -->
        <IndicatorLibrary @indicator-selected="handleIndicatorSelected" />
        
        <!-- Current Indicators -->
        <div class="mt-6">
          <h4 class="text-sm font-semibold text-gray-400 mb-3">Chỉ báo đang sử dụng</h4>
          <div class="space-y-2">
            <div
              v-for="indicator in activeIndicators"
              :key="indicator.id"
              class="flex items-center justify-between p-2 bg-slate-700/50 rounded"
            >
              <span class="text-sm text-white">{{ indicator.name }}</span>
              <button
                @click="removeIndicator(indicator.id)"
                class="text-red-400 hover:text-red-300"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Technical Data -->
    <div v-if="!analysisStore.isLoading && Object.keys(technicalData).length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="(value, key) in technicalData"
        :key="key"
        class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-lg p-4 border border-purple-500/20 hover:border-purple-400/40 transition-all"
      >
        <div class="text-sm text-gray-400 mb-1">{{ formatKey(key) }}</div>
        <div class="text-xl font-bold text-white">{{ formatValue(value) }}</div>
        <div v-if="getValueChange(value)" class="text-xs mt-1" :class="getValueChange(value) > 0 ? 'text-green-400' : 'text-red-400'">
          <i :class="getValueChange(value) > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'" class="mr-1"></i>
          {{ Math.abs(getValueChange(value)) }}%
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!analysisStore.isLoading && Object.keys(technicalData).length === 0" class="text-center py-8">
      <i class="fas fa-chart-line text-4xl text-purple-400/50 mb-4"></i>
      <p class="text-gray-400">Chưa có dữ liệu phân tích kỹ thuật</p>
    </div>

    <!-- Drawing Tools -->
    <DrawingTools @drawing-complete="handleDrawingComplete" />
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useAnalysisStore } from '../../stores/analysis';
// Use dynamic import for lightweight-charts to avoid build issues
// import { createChart } from 'lightweight-charts';
import IndicatorLibrary from './IndicatorLibrary.vue';
import DrawingTools from './DrawingTools.vue';

const analysisStore = useAnalysisStore();
const chartContainer = ref(null);
const chart = ref(null);
const candlestickSeries = ref(null);
const timeFrame = ref('1h');
const activeIndicators = ref([]);
const updateInterval = ref(null);

const technicalData = computed(() => {
  return analysisStore.technicalData.indicators || {};
});

const handleTimeFrameChange = () => {
  analysisStore.setTimeFrame(timeFrame.value);
  // Refetch data
  analysisStore.fetchTechnicalAnalysis().then(() => {
    updateChart();
  });
};

const retryLoad = () => {
  analysisStore.fetchTechnicalAnalysis().then(() => {
    updateChart();
  });
};

const handleIndicatorSelected = (indicator) => {
  if (!activeIndicators.value.find(i => i.id === indicator.id)) {
    activeIndicators.value.push(indicator);
    // Apply indicator to chart
    applyIndicator(indicator);
  }
};

const removeIndicator = (indicatorId) => {
  activeIndicators.value = activeIndicators.value.filter(i => i.id !== indicatorId);
  // Remove from chart
  updateChart();
};

const applyIndicator = (indicator) => {
  // Apply indicator logic here
  updateChart();
};

const handleDrawingComplete = (drawing) => {
  // Save drawing
  console.log('Drawing completed:', drawing);
};

const updateChart = () => {
  if (!chart.value || !chartContainer.value) return;
  
  const data = analysisStore.technicalData.candles || analysisStore.technicalData.data || [];
  
  if (data.length > 0 && candlestickSeries.value) {
    // Format data for lightweight-charts
    const formattedData = data.map(item => ({
      time: item.time || item.timestamp || item.date,
      open: parseFloat(item.open || item.o),
      high: parseFloat(item.high || item.h),
      low: parseFloat(item.low || item.l),
      close: parseFloat(item.close || item.c)
    })).filter(item => !isNaN(item.open) && !isNaN(item.high) && !isNaN(item.low) && !isNaN(item.close));
    
    if (formattedData.length > 0) {
      candlestickSeries.value.setData(formattedData);
      chart.value.timeScale().fitContent();
    }
  }
};

const formatKey = (key) => {
  const labels = {
    rsi: 'RSI',
    macd: 'MACD',
    bollinger: 'Bollinger Bands',
    moving_averages: 'Moving Averages',
    support: 'Support',
    resistance: 'Resistance',
    trend: 'Trend'
  };
  return labels[key] || key;
};

const formatValue = (value) => {
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      return value.length > 0 ? value[0] : '-';
    }
    return JSON.stringify(value);
  }
  if (typeof value === 'number') {
    return value.toFixed(2);
  }
  return value || '-';
};

const getValueChange = (value) => {
  // This would typically compare with previous value
  // For now, return null to hide change indicator
  return null;
};

const initChart = async () => {
  if (!chartContainer.value || chart.value) return;

  // Dynamic import lightweight-charts to avoid build issues
  let createChartFn;
  try {
    const chartModule = await import('lightweight-charts');
    createChartFn = chartModule.createChart;
  } catch (error) {
    console.error('Failed to load lightweight-charts:', error);
    // Return early if chart library cannot be loaded
    return;
  }
  
  chart.value = createChartFn(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { color: '#1e293b' },
      textColor: '#d1d5db',
    },
    grid: {
      vertLines: { color: '#334155', style: 1 },
      horzLines: { color: '#334155', style: 1 },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
    crosshair: {
      mode: 0,
    },
  });

  // Add candlestick series
  candlestickSeries.value = chart.value.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#ef4444',
    borderVisible: false,
    wickUpColor: '#10b981',
    wickDownColor: '#ef4444',
  });

  // Handle resize
  const resizeObserver = new ResizeObserver(() => {
    if (chart.value && chartContainer.value) {
      chart.value.applyOptions({ width: chartContainer.value.clientWidth });
    }
  });
  resizeObserver.observe(chartContainer.value);

  // Update chart with initial data
  updateChart();
};

const startRealTimeUpdates = () => {
  // Clear existing interval
  if (updateInterval.value) {
    clearInterval(updateInterval.value);
  }

  // Set up real-time updates every 5 seconds
  updateInterval.value = setInterval(() => {
    if (!analysisStore.isLoading) {
      analysisStore.fetchTechnicalAnalysis().then(() => {
        updateChart();
      });
    }
  }, 5000);
};

const stopRealTimeUpdates = () => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value);
    updateInterval.value = null;
  }
};

onMounted(async () => {
  // Fetch technical analysis first
  await analysisStore.fetchTechnicalAnalysis();
  
  // Initialize chart after data is loaded
  await nextTick();
  initChart();
  
  // Start real-time updates
  startRealTimeUpdates();
});

watch(() => analysisStore.selectedSymbol, async () => {
  await analysisStore.fetchTechnicalAnalysis();
  updateChart();
});

watch(() => analysisStore.technicalData, () => {
  updateChart();
}, { deep: true });

// Cleanup on unmount
onUnmounted(() => {
  stopRealTimeUpdates();
  if (chart.value) {
    chart.value.remove();
    chart.value = null;
  }
});
</script>

<style scoped>
.chart-container {
  position: relative;
}
</style>

