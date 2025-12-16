<template>
  <section class="mb-8">
    <div class="market-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-white">Biểu đồ TradingView</h2>
        <div class="flex items-center space-x-2">
          <select
            v-model="selectedTimeframe"
            @change="updateTimeframe"
            class="market-search-input px-3 py-1 text-sm"
          >
            <option value="1">1 phút</option>
            <option value="5">5 phút</option>
            <option value="15">15 phút</option>
            <option value="60">1 giờ</option>
            <option value="240">4 giờ</option>
            <option value="D">1 ngày</option>
          </select>
        </div>
      </div>
      
      <div class="w-full h-96 bg-slate-900 rounded-lg overflow-hidden">
        <!-- TradingView Widget -->
        <div
          v-if="showTradingView"
          ref="tradingViewContainer"
          class="w-full h-full"
        ></div>
        
        <!-- Lightweight Charts Fallback -->
        <div
          v-else-if="!chartError"
          ref="chartContainer"
          class="w-full h-full"
        ></div>
        
        <!-- Error Fallback UI -->
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-gray-400"
        >
          <div class="text-center">
            <p class="mb-2">Không thể tải biểu đồ</p>
            <button
              @click="retryChartInitialization"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Thử lại
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useMarketStore } from '../../stores/market';

const marketStore = useMarketStore();
const tradingViewContainer = ref(null);
const chartContainer = ref(null);
const selectedTimeframe = ref('60');
const showTradingView = ref(false);
const chartError = ref(false);
let chart = null;
let candlestickSeries = null; // hold reference for updates

const initializeTradingView = () => {
  // TradingView widget integration
  // Note: This requires TradingView widget script to be loaded
  if (window.TradingView && tradingViewContainer.value) {
    showTradingView.value = true;
    new window.TradingView.widget({
      autosize: true,
      symbol: marketStore.selectedInstrument?.symbol || 'BINANCE:BTCUSDT',
      interval: selectedTimeframe.value,
      theme: 'dark',
      style: '1',
      locale: 'vi',
      toolbar_bg: '#1a0b2e',
      enable_publishing: false,
      hide_top_toolbar: true,
      hide_legend: false,
      save_image: false,
      container_id: tradingViewContainer.value,
    });
  } else {
    // Fallback to Lightweight Charts
    initializeLightweightChart();
  }
};

const initializeLightweightChart = async () => {
  // Reset error state
  chartError.value = false;
  
  // Clean up existing chart if any
  if (chart) {
    try {
      chart.remove();
    } catch (e) {
      console.warn('Error removing old chart:', e);
    }
    chart = null;
    candlestickSeries = null;
  }
  
  // Validate container exists
  if (!chartContainer.value) {
    console.error('Chart container not available');
    chartError.value = true;
    return;
  }
  
  // Validate container has dimensions
  const width = chartContainer.value.clientWidth;
  const height = chartContainer.value.clientHeight;
  
  if (width <= 0 || height <= 0) {
    console.warn('Chart container has zero dimensions, retrying...');
    // Retry after a short delay
    setTimeout(() => {
      initializeLightweightChart();
    }, 100);
    return;
  }
  
  try {
      // Lazy import to avoid SSR/ESM interop issues
      // Prefer named import to avoid ESM/interop surprises; fall back to default export and ESM bundle if needed
      let createChartFn = null;
      try {
        const chartLib = await import('lightweight-charts');
        createChartFn = chartLib.createChart || chartLib.default?.createChart || chartLib?.createChart;
      } catch (e) {
        console.warn('Default lightweight-charts import failed, will try ESM build:', e);
      }

      // If main import failed, try production build
      if (typeof createChartFn !== 'function') {
        try {
          const prod = await import('lightweight-charts');
          createChartFn = prod.createChart || prod.default?.createChart;
        } catch (e) {
          console.warn('Production lightweight-charts import also failed:', e);
        }
      }

      if (typeof createChartFn !== 'function') {
        throw new Error('createChart is not available from lightweight-charts import');
      }

      showTradingView.value = false;

      // Create chart with error handling
      chart = createChartFn(chartContainer.value, {
        width: width,
        height: height,
        layout: {
          background: { color: '#1a0b2e' },
          textColor: '#d1d5db',
        },
        grid: {
          vertLines: { color: '#374151' },
          horzLines: { color: '#374151' },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });
    // Validate chart object was created
    if (!chart) {
      throw new Error('Chart object is null after createChart');
    }

    // Create candlestick series with robust fallbacks
    const seriesOptions = {
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    };

    try {
      if (typeof chart.addCandlestickSeries !== 'function') {
        throw new Error('addCandlestickSeries is not a function on chart object');
      }
      candlestickSeries = chart.addCandlestickSeries(seriesOptions);

      if (!candlestickSeries) {
        throw new Error('Candlestick series is null after addCandlestickSeries');
      }
    } catch (seriesError) {
      console.warn('Primary candlestick series creation failed:', seriesError);

      // Attempt alternate import and recreate chart (rare edge-case for certain bundlers)
      try {
        // Remove any partially created chart
        if (chart) {
          try { chart.remove(); } catch (e) { /* ignore */ }
          chart = null;
          candlestickSeries = null;
        }

        const alt = await import('lightweight-charts');
        const altCreate = alt.createChart || alt.default?.createChart;
        if (typeof altCreate !== 'function') {
          throw new Error('Alternate createChart is not available');
        }

        chart = altCreate(chartContainer.value, {
          width: width,
          height: height,
          layout: {
            background: { color: '#1a0b2e' },
            textColor: '#d1d5db',
          },
          grid: {
            vertLines: { color: '#374151' },
            horzLines: { color: '#374151' },
          },
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
          },
        });

        if (typeof chart.addCandlestickSeries !== 'function') {
          throw new Error('addCandlestickSeries is still not available after alternate import');
        }

        candlestickSeries = chart.addCandlestickSeries(seriesOptions);
        if (!candlestickSeries) {
          throw new Error('Candlestick series null after alternate creation');
        }
      } catch (fallbackError) {
        console.error('Fallback candlestick creation failed:', fallbackError);
        throw fallbackError;
      }
    }
    
    // Fetch real market data from API - no mock data
    await fetchRealMarketData();
    
    // Fit content with error handling
    if (chart && typeof chart.timeScale === 'function') {
      const timeScale = chart.timeScale();
      if (timeScale && typeof timeScale.fitContent === 'function') {
        timeScale.fitContent();
      }
    }
    
  } catch (error) {
    console.error('Error initializing lightweight chart:', error);
    chartError.value = true;
    
    // Clean up on error
    if (chart) {
      try {
        chart.remove();
      } catch (e) {
        console.warn('Error removing chart on cleanup:', e);
      }
      chart = null;
    }
    candlestickSeries = null;
  }
};

async function fetchRealMarketData() {
  if (!marketStore.selectedInstrument || !candlestickSeries) return;
  
  try {
    const symbol = marketStore.selectedInstrument.symbol;
    const response = await fetch(`/api/market/historical-data/${symbol}?timeframe=1h&limit=100`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.data && data.data.length > 0) {
        const realData = data.data.map(candle => ({
          time: new Date(candle.timestamp).getTime() / 1000,
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
        }));
        
        // Validate setData method exists
        if (candlestickSeries && typeof candlestickSeries.setData === 'function') {
          candlestickSeries.setData(realData);
        }
        return;
      }
    }
  } catch (error) {
    console.warn('Could not fetch real market data:', error);
  }
  
  // If no real data available, show empty chart
  if (candlestickSeries && typeof candlestickSeries.setData === 'function') {
    candlestickSeries.setData([]);
  }
}

const updateTimeframe = async () => {
  if (chart) {
    try {
      chart.remove();
    } catch (e) {
      console.warn('Error removing chart:', e);
    }
    chart = null;
    candlestickSeries = null;
  }
  await initializeLightweightChart();
};

const retryChartInitialization = async () => {
  chartError.value = false;
  await nextTick();
  await initializeLightweightChart();
};

watch(() => marketStore.selectedInstrument, async () => {
  if (chart) {
    try {
      chart.remove();
    } catch (e) {
      console.warn('Error removing chart:', e);
    }
    chart = null;
    candlestickSeries = null;
  }
  await initializeLightweightChart();
});

onMounted(async () => {
  // Wait for DOM to be ready
  await nextTick();
  
  // Try TradingView first, fallback to Lightweight Charts
  setTimeout(async () => {
    try {
      initializeTradingView();
    } catch (error) {
      console.error('Error initializing TradingView, falling back to Lightweight Charts:', error);
      await initializeLightweightChart();
    }
  }, 100);
});

onUnmounted(() => {
  if (chart) {
    chart.remove();
    chart = null;
    candlestickSeries = null;
  }
});
</script>

