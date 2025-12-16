<template>
  <div class="market-preview-page">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Market Preview</h1>
        <p class="text-white/60">
          Real-time market data và chart preview cho tất cả symbols
        </p>
      </div>
      <div class="flex items-center gap-4">
        <!-- Symbol Selector -->
        <Select
          v-model="selectedSymbol"
          :options="symbolOptions"
          placeholder="Chọn symbol"
          class="w-48"
          @update:modelValue="handleSymbolChange"
        />
        
        <!-- Connection Status -->
        <div class="flex items-center gap-2 text-sm">
          <i :class="[
            'fas',
            marketStore.isConnected ? 'fa-circle text-green-400' : 'fa-circle text-red-400'
          ]"></i>
          <span :class="marketStore.isConnected ? 'text-green-400' : 'text-red-400'">
            {{ marketStore.isConnected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Market Data Cards -->
    <div v-if="selectedSymbol" class="mb-6">
      <MarketDataCards
        :symbol="selectedSymbol"
        :compact="false"
      />
    </div>

    <!-- Chart Section -->
    <div v-if="selectedSymbol" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Chart -->
      <div class="lg:col-span-2">
        <Card title="Real-time Chart">
          <div class="chart-controls mb-4">
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <label class="text-sm text-white/80">Timeframe:</label>
                <Select
                  v-model="selectedTimeframe"
                  :options="timeframeOptions"
                  class="w-24"
                  @update:modelValue="handleTimeframeChange"
                />
              </div>
              
              <div class="flex items-center gap-2">
                <button
                  :class="['chart-type-btn', { active: chartType === 'candlestick' }]"
                  @click="chartType = 'candlestick'"
                >
                  <i class="fas fa-chart-candlestick"></i>
                  Candles
                </button>
                <button
                  :class="['chart-type-btn', { active: chartType === 'line' }]"
                  @click="chartType = 'line'"
                >
                  <i class="fas fa-chart-line"></i>
                  Line
                </button>
              </div>
            </div>
          </div>
          
          <MarketChartPreview
            :symbol="selectedSymbol"
            :compact="false"
            :height="500"
          />
        </Card>
      </div>

      <!-- Side Panel -->
      <div class="space-y-6">
        <!-- Market Stats -->
        <Card title="Market Statistics">
          <div v-if="marketData" class="space-y-4">
            <div class="stat-item">
              <div class="stat-label">24h Change</div>
              <div :class="['stat-value', {
                'text-green-400': marketData.change_percent_24h >= 0,
                'text-red-400': marketData.change_percent_24h < 0
              }]">
                {{ marketData.change_percent_24h >= 0 ? '+' : '' }}{{ formatPercent(marketData.change_percent_24h) }}
              </div>
            </div>
            
            <div class="stat-item">
              <div class="stat-label">24h Volume</div>
              <div class="stat-value">${{ formatLargeNumber(marketData.volume_24h) }}</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-label">Market Cap</div>
              <div class="stat-value">${{ formatLargeNumber(marketData.market_cap) }}</div>
            </div>
            
            <div v-if="marketData.fdv > 0" class="stat-item">
              <div class="stat-label">FDV</div>
              <div class="stat-value">${{ formatLargeNumber(marketData.fdv) }}</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-label">Vol/Mkt Cap</div>
              <div class="stat-value">{{ formatPercent(marketData.vol_mkt_cap_24h) }}</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-label">24h Range</div>
              <div class="stat-value">
                <span class="text-green-400">${{ formatPrice(marketData.high_24h) }}</span>
                <span class="text-white/60 mx-2">-</span>
                <span class="text-red-400">${{ formatPrice(marketData.low_24h) }}</span>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-4 text-white/60">
            <i class="fas fa-spinner fa-spin"></i>
            <span class="ml-2">Đang tải...</span>
          </div>
        </Card>

        <!-- Supply Information -->
        <Card v-if="marketData && marketData.supply" title="Supply Information">
          <div class="space-y-3">
            <div class="supply-item">
              <div class="supply-label">Circulating</div>
              <div class="supply-value">{{ formatNumber(marketData.supply.circulating) }}</div>
            </div>
            
            <div v-if="marketData.supply.total !== marketData.supply.circulating" class="supply-item">
              <div class="supply-label">Total</div>
              <div class="supply-value">{{ formatNumber(marketData.supply.total) }}</div>
            </div>
            
            <div v-if="marketData.supply.max > 0" class="supply-item">
              <div class="supply-label">Max</div>
              <div class="supply-value">{{ formatNumber(marketData.supply.max) }}</div>
            </div>
            
            <!-- Supply Progress Bar -->
            <div v-if="marketData.supply.max > 0" class="supply-progress">
              <div class="progress-label">
                <span class="text-xs text-white/60">Circulating Supply</span>
                <span class="text-xs text-white/60">
                  {{ ((marketData.supply.circulating / marketData.supply.max) * 100).toFixed(1) }}%
                </span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: `${(marketData.supply.circulating / marketData.supply.max) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </Card>

        <!-- Last Update -->
        <Card title="Information">
          <div class="space-y-3 text-sm">
            <div class="info-item">
              <div class="info-label">Last Update</div>
              <div class="info-value">{{ formatTimestamp(marketData?.timestamp) }}</div>
            </div>
            
            <div class="info-item">
              <div class="info-label">Data Source</div>
              <div class="info-value">Trading Simulator</div>
            </div>
            
            <div class="info-item">
              <div class="info-label">Update Frequency</div>
              <div class="info-value">Real-time (100ms)</div>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- No Symbol Selected -->
    <div v-else class="text-center py-16">
      <i class="fas fa-chart-line text-6xl text-white/20 mb-4"></i>
      <h3 class="text-xl font-semibold text-white mb-2">Chọn Symbol để Xem Preview</h3>
      <p class="text-white/60">Chọn một symbol từ dropdown để xem market data và chart real-time</p>
    </div>

    <!-- Error State -->
    <div v-if="marketStore.hasError" class="fixed bottom-4 right-4 bg-red-500/20 border border-red-500/30 rounded-lg p-4 max-w-md">
      <div class="flex items-center gap-3">
        <i class="fas fa-exclamation-triangle text-red-400"></i>
        <div>
          <div class="text-sm font-medium text-red-400">Connection Error</div>
          <div class="text-xs text-red-300">{{ marketStore.error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useMarketPreviewStore } from '../store/marketPreview';
import Card from '../components/ui/Card.vue';
import Select from '../components/ui/Select.vue';
import MarketChartPreview from '../components/market/MarketChartPreview.vue';
import MarketDataCards from '../components/market/MarketDataCards.vue';

// Store
const marketStore = useMarketPreviewStore();

// State
const selectedSymbol = ref('');
const selectedTimeframe = ref('1h');
const chartType = ref('candlestick');

// Available symbols
const availableSymbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'];

// Options
const symbolOptions = computed(() => 
  availableSymbols.map(symbol => ({
    label: symbol,
    value: symbol
  }))
);

const timeframeOptions = [
  { label: '1H', value: '1h' },
  { label: '4H', value: '4h' },
  { label: '1D', value: '1d' },
  { label: '1W', value: '1w' }
];

// Computed
const marketData = computed(() => 
  selectedSymbol.value ? marketStore.marketData[selectedSymbol.value] : null
);

// Methods
const handleSymbolChange = (symbol) => {
  if (symbol) {
    // Unsubscribe from previous symbol
    if (selectedSymbol.value) {
      marketStore.unsubscribeFromSymbol(selectedSymbol.value);
    }
    
    // Subscribe to new symbol
    marketStore.subscribeToSymbol(symbol);
    
    // Fetch initial data
    marketStore.fetchMarketData(symbol);
  }
};

const handleTimeframeChange = (timeframe) => {
  selectedTimeframe.value = timeframe;
  // Chart component will handle timeframe change
};

// Formatting functions
const formatPrice = (price) => {
  if (price === 0) return '0.00';
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatPercent = (percent) => {
  return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
};

const formatLargeNumber = (num) => {
  if (num === 0) return '0';
  
  const abs = Math.abs(num);
  
  if (abs >= 1e12) {
    return `${(num / 1e12).toFixed(2)}T`;
  } else if (abs >= 1e9) {
    return `${(num / 1e9).toFixed(2)}B`;
  } else if (abs >= 1e6) {
    return `${(num / 1e6).toFixed(2)}M`;
  } else if (abs >= 1e3) {
    return `${(num / 1e3).toFixed(2)}K`;
  } else {
    return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
};

const formatNumber = (num) => {
  if (num === 0) return '0';
  return num.toLocaleString('en-US');
};

const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  return new Date(timestamp).toLocaleString();
};

// Lifecycle
onMounted(() => {
  // Set default symbol
  selectedSymbol.value = availableSymbols[0];
  handleSymbolChange(selectedSymbol.value);
});

onUnmounted(() => {
  // Cleanup
  if (selectedSymbol.value) {
    marketStore.unsubscribeFromSymbol(selectedSymbol.value);
  }
});
</script>

<style scoped>
.market-preview-page {
  @apply space-y-6;
}

.chart-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-type-btn {
  @apply px-3 py-2 text-xs font-medium rounded transition-colors;
  @apply text-white/60 hover:text-white hover:bg-white/10;
}

.chart-type-btn.active {
  @apply text-white bg-blue-500/20 border border-blue-500/30;
}

.stat-item {
  @apply flex items-center justify-between py-2 border-b border-white/10 last:border-0;
}

.stat-label {
  @apply text-sm text-white/60;
}

.stat-value {
  @apply text-sm font-medium text-white;
}

.supply-item {
  @apply flex items-center justify-between py-2;
}

.supply-label {
  @apply text-sm text-white/60;
}

.supply-value {
  @apply text-sm font-medium text-white;
}

.supply-progress {
  @apply pt-2;
}

.progress-label {
  @apply flex items-center justify-between mb-1;
}

.progress-bar {
  @apply w-full h-2 bg-white/10 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-500 rounded-full transition-all duration-300;
}

.info-item {
  @apply flex items-center justify-between py-2;
}

.info-label {
  @apply text-xs text-white/60;
}

.info-value {
  @apply text-xs text-white/80;
}

/* Responsive */
@media (max-width: 1024px) {
  .market-preview-page .grid {
    @apply grid-cols-1;
  }
}

@media (max-width: 768px) {
  .chart-controls {
    @apply flex-col items-start gap-3;
  }
  
  .chart-controls .flex {
    @apply w-full;
  }
}
</style>
