<template>
  <div class="market-chart-preview" :class="{ compact }">
    <div class="chart-container" :style="{ height: `${height}px` }">
      <div ref="chartContainer" class="chart"></div>
      <div v-if="loading" class="chart-loading">
        <i class="fas fa-spinner fa-spin"></i>
        <span>Đang tải...</span>
      </div>
    </div>
    
    <!-- Timeframe selector (only for non-compact mode) -->
    <div v-if="!compact" class="timeframe-selector">
      <button
        v-for="tf in timeframes"
        :key="tf.value"
        :class="['timeframe-btn', { active: selectedTimeframe === tf.value }]"
        @click="changeTimeframe(tf.value)"
      >
        {{ tf.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useMarketPreviewStore } from '../../store/marketPreview';

// Props
const props = defineProps({
  symbol: {
    type: String,
    required: true
  },
  compact: {
    type: Boolean,
    default: false
  },
  height: {
    type: Number,
    default: 400
  }
});

// Store
const marketStore = useMarketPreviewStore();

// Refs
const chartContainer = ref(null);
const chart = ref(null);
const loading = ref(false);
const selectedTimeframe = ref('1h');

// Timeframes
const timeframes = [
  { label: '1H', value: '1h' },
  { label: '4H', value: '4h' },
  { label: '1D', value: '1d' },
  { label: '1W', value: '1w' }
];

// Initialize TradingView Lightweight Charts
const initChart = async () => {
  if (!chartContainer.value) return;
  
  try {
    // Dynamic import to avoid SSR issues
    const { createChart } = await import('lightweight-charts');
    
    // Create chart instance
    chart.value = createChart(chartContainer.value, {
      width: chartContainer.value.clientWidth,
      height: props.height,
      layout: {
        background: { color: 'transparent' },
        textColor: '#9CA3AF',
        fontSize: props.compact ? 10 : 12
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.1)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      crosshair: {
        mode: 1,
        vertLine: { color: 'rgba(255, 255, 255, 0.3)' },
        horzLine: { color: 'rgba(255, 255, 255, 0.3)' }
      },
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textColor: '#9CA3AF'
      },
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textColor: '#9CA3AF',
        timeVisible: true,
        secondsVisible: false
      }
    });

    // Add candlestick series
    const candlestickSeries = chart.value.addCandlestickSeries({
      upColor: '#10B981',
      downColor: '#EF4444',
      borderDownColor: '#EF4444',
      borderUpColor: '#10B981',
      wickDownColor: '#EF4444',
      wickUpColor: '#10B981',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01
      }
    });

    // Add volume series (bottom)
    const volumeSeries = chart.value.addHistogramSeries({
      color: 'rgba(59, 130, 246, 0.5)',
      priceFormat: {
        type: 'volume'
      },
      priceScaleId: 'volume',
      scaleMargins: {
        top: 0.85,
        bottom: 0
      }
    });

    // Store series references
    chart.value.candlestickSeries = candlestickSeries;
    chart.value.volumeSeries = volumeSeries;

    // Load initial data
    await loadChartData();

  } catch (error) {
    console.error('Failed to initialize chart:', error);
  }
};

// Load chart data
const loadChartData = async () => {
  if (!chart.value) return;
  
  loading.value = true;
  try {
    // Get candle data from store
    const candles = await marketStore.getCandles(props.symbol, selectedTimeframe.value);
    
    if (candles.length > 0) {
      // Format data for TradingView
      const candlestickData = candles.map(candle => ({
        time: new Date(candle.timestamp).getTime() / 1000,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close
      }));

      const volumeData = candles.map(candle => ({
        time: new Date(candle.timestamp).getTime() / 1000,
        value: candle.volume,
        color: candle.close >= candle.open ? '#10B981' : '#EF4444'
      }));

      // Update chart
      chart.value.candlestickSeries.setData(candlestickData);
      chart.value.volumeSeries.setData(volumeData);
      
      // Fit content
      chart.value.timeScale().fitContent();
    }
  } catch (error) {
    console.error('Failed to load chart data:', error);
  } finally {
    loading.value = false;
  }
};

// Change timeframe
const changeTimeframe = (timeframe) => {
  selectedTimeframe.value = timeframe;
  loadChartData();
};

// Handle real-time updates
const handleRealTimeUpdate = (data) => {
  if (!chart.value || data.symbol !== props.symbol) return;
  
  try {
    // Update with new candle data
    if (data.candle) {
      const candlestickData = {
        time: new Date(data.candle.timestamp).getTime() / 1000,
        open: data.candle.open,
        high: data.candle.high,
        low: data.candle.low,
        close: data.candle.close
      };

      const volumeData = {
        time: new Date(data.candle.timestamp).getTime() / 1000,
        value: data.candle.volume,
        color: data.candle.close >= data.candle.open ? '#10B981' : '#EF4444'
      };

      // Update chart with new data
      chart.value.candlestickSeries.update(candlestickData);
      chart.value.volumeSeries.update(volumeData);
    }
  } catch (error) {
    console.error('Failed to update chart with real-time data:', error);
  }
};

// Handle resize
const handleResize = () => {
  if (chart.value && chartContainer.value) {
    chart.value.applyOptions({
      width: chartContainer.value.clientWidth
    });
  }
};

// Watch symbol changes
watch(() => props.symbol, () => {
  loadChartData();
});

// Watch store updates
watch(() => marketStore.candles[props.symbol], () => {
  loadChartData();
}, { deep: true });

// Lifecycle
onMounted(async () => {
  // Subscribe to WebSocket updates
  marketStore.subscribeToSymbol(props.symbol);
  
  // Listen for real-time updates
  marketStore.$onAction(({ name, args }) => {
    if (name === 'handleWebSocketMessage') {
      const [event, data] = args;
      if (event === 'candle_update' && data.symbol === props.symbol) {
        handleRealTimeUpdate(data);
      }
    }
  });

  await nextTick();
  await initChart();
  
  // Add resize listener
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  // Unsubscribe from WebSocket
  marketStore.unsubscribeFromSymbol(props.symbol);
  
  // Cleanup chart
  if (chart.value) {
    chart.value.remove();
    chart.value = null;
  }
  
  // Remove resize listener
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.market-chart-preview {
  @apply bg-white/5 border border-white/10 rounded-lg overflow-hidden;
}

.market-chart-preview.compact {
  @apply border-white/5;
}

.chart-container {
  @apply relative;
}

.chart {
  @apply w-full h-full;
}

.chart-loading {
  @apply absolute inset-0 flex items-center justify-center bg-black/50 text-white/80;
  @apply flex-col gap-2;
}

.timeframe-selector {
  @apply flex items-center gap-1 p-2 border-t border-white/10;
  @apply bg-black/20;
}

.timeframe-btn {
  @apply px-3 py-1 text-xs font-medium rounded transition-colors;
  @apply text-white/60 hover:text-white hover:bg-white/10;
}

.timeframe-btn.active {
  @apply text-white bg-blue-500/20 border border-blue-500/30;
}

/* Responsive */
@media (max-width: 768px) {
  .timeframe-selector {
    @apply justify-center;
  }
  
  .timeframe-btn {
    @apply px-2 py-1 text-xs;
  }
}
</style>
