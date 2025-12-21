<template>
  <div class="tradingview-chart-wrapper">
    <div class="chart-header">
      <h3>{{ displaySymbol }} - Real-Time Chart</h3>
      <div class="chart-controls">
        <select v-model="selectedInterval" @change="updateInterval" class="interval-select">
          <option value="1">1m</option>
          <option value="5">5m</option>
          <option value="15">15m</option>
          <option value="60">1h</option>
          <option value="240">4h</option>
          <option value="D">1D</option>
        </select>
      </div>
    </div>
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
});

const chartContainer = ref(null);
const selectedInterval = ref('15');
let tvWidget = null;

const displaySymbol = ref(props.symbol);

// Map our symbols to TradingView symbols
const getTradingViewSymbol = (symbol) => {
  const symbolMap = {
    'BTC': 'BINANCE:BTCUSDT',
    'ETH': 'BINANCE:ETHUSDT',
    'BNB': 'BINANCE:BNBUSDT',
    'SOL': 'BINANCE:SOLUSDT',
    'XRP': 'BINANCE:XRPUSDT',
    'BTCUSDT': 'BINANCE:BTCUSDT',
    'ETHUSDT': 'BINANCE:ETHUSDT',
    'EUR/USD': 'FX:EURUSD',
    'GBP/USD': 'FX:GBPUSD',
    'USD/JPY': 'FX:USDJPY',
    'GOLD': 'TVC:GOLD',
    'XAU': 'TVC:GOLD',
    'SILVER': 'TVC:SILVER',
    'XAG': 'TVC:SILVER'
  };
  
  return symbolMap[symbol] || 'BINANCE:BTCUSDT';
};

const initChart = () => {
  if (!chartContainer.value) return;
  
  // Load TradingView library if not already loaded
  if (!window.TradingView) {
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => createWidget();
    document.head.appendChild(script);
  } else {
    createWidget();
  }
};

const createWidget = () => {
  if (!window.TradingView || !chartContainer.value) return;
  
  const tradingViewSymbol = getTradingViewSymbol(props.symbol);
  displaySymbol.value = props.symbol;
  
  tvWidget = new window.TradingView.widget({
    autosize: true,
    symbol: tradingViewSymbol,
    interval: selectedInterval.value,
    container: chartContainer.value,
    datafeed: new window.Datafeeds.UDFCompatibleDatafeed('https://demo-feed-data.tradingview.com'),
    library_path: 'https://unpkg.com/tradingview-charting-library@25.0.0/charting_library/',
    locale: 'vi',
    disabled_features: ['use_localstorage_for_settings'],
    enabled_features: ['study_templates'],
    theme: 'dark',
    style: '1',
    toolbar_bg: '#1e293b',
    enable_publishing: false,
    hide_side_toolbar: false,
    allow_symbol_change: true,
    studies_overrides: {},
    overrides: {
      'paneProperties.background': '#0f172a',
      'paneProperties.backgroundType': 'solid',
      'mainSeriesProperties.candleStyle.upColor': '#10b981',
      'mainSeriesProperties.candleStyle.downColor': '#ef4444',
      'mainSeriesProperties.candleStyle.borderUpColor': '#10b981',
      'mainSeriesProperties.candleStyle.borderDownColor': '#ef4444',
      'mainSeriesProperties.candleStyle.wickUpColor': '#10b981',
      'mainSeriesProperties.candleStyle.wickDownColor': '#ef4444',
    },
  });
  
  console.log('[TradingViewChart] Chart initialized for', tradingViewSymbol);
};

const updateInterval = () => {
  if (tvWidget && tvWidget.chart) {
    tvWidget.chart().setResolution(selectedInterval.value);
    console.log('[TradingViewChart] Interval changed to', selectedInterval.value);
  }
};

watch(() => props.symbol, (newSymbol) => {
  if (tvWidget && tvWidget.chart) {
    const tradingViewSymbol = getTradingViewSymbol(newSymbol);
    displaySymbol.value = newSymbol;
    tvWidget.chart().setSymbol(tradingViewSymbol, () => {
      console.log('[TradingViewChart] Symbol changed to', tradingViewSymbol);
    });
  }
});

onMounted(() => {
  initChart();
});

onUnmounted(() => {
  if (tvWidget) {
    tvWidget.remove();
    tvWidget = null;
  }
});
</script>

<style scoped>
.tradingview-chart-wrapper {
  width: 100%;
  height: 600px;
  background: #0f172a;
  border-radius: 8px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #1e293b;
  border-bottom: 1px solid #334155;
}

.chart-header h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 18px;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.interval-select {
  padding: 8px 12px;
  background: #0f172a;
  color: #f1f5f9;
  border: 1px solid #334155;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.interval-select:hover {
  border-color: #3b82f6;
}

.interval-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.chart-container {
  width: 100%;
  height: calc(100% - 60px);
}
</style>
