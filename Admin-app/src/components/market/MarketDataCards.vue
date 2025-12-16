<template>
  <div class="market-data-cards" :class="{ compact }">
    <!-- Price Card -->
    <div class="data-card price-card">
      <div class="card-header">
        <span class="card-title">{{ symbol }}</span>
        <span v-if="!compact" class="card-subtitle">Current Price</span>
      </div>
      <div class="card-content">
        <div class="price-display">
          <span class="price">${{ formatPrice(marketData.price) }}</span>
          <span 
            :class="['change', { positive: marketData.change_percent_24h >= 0, negative: marketData.change_percent_24h < 0 }]"
          >
            <i :class="marketData.change_percent_24h >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ formatPercent(marketData.change_percent_24h) }}
          </span>
        </div>
        <div v-if="!compact" class="price-details">
          <span class="change-amount">
            {{ marketData.change_24h >= 0 ? '+' : '' }}{{ formatPrice(marketData.change_24h) }}
          </span>
          <span class="timeframe">24h</span>
        </div>
      </div>
    </div>

    <!-- Market Cap Card -->
    <div class="data-card">
      <div class="card-header">
        <span class="card-title">Market Cap</span>
        <i class="fas fa-chart-pie card-icon"></i>
      </div>
      <div class="card-content">
        <span class="value">${{ formatLargeNumber(marketData.market_cap) }}</span>
      </div>
    </div>

    <!-- Volume 24h Card -->
    <div class="data-card">
      <div class="card-header">
        <span class="card-title">Volume 24h</span>
        <i class="fas fa-chart-bar card-icon"></i>
      </div>
      <div class="card-content">
        <span class="value">${{ formatLargeNumber(marketData.volume_24h) }}</span>
      </div>
    </div>

    <!-- FDV Card (Fully Diluted Valuation) -->
    <div v-if="!compact && marketData.fdv > 0" class="data-card">
      <div class="card-header">
        <span class="card-title">FDV</span>
        <i class="fas fa-coins card-icon"></i>
      </div>
      <div class="card-content">
        <span class="value">${{ formatLargeNumber(marketData.fdv) }}</span>
      </div>
    </div>

    <!-- Vol/Mkt Cap Ratio Card -->
    <div v-if="!compact" class="data-card">
      <div class="card-header">
        <span class="card-title">Vol/Mkt Cap</span>
        <i class="fas fa-percentage card-icon"></i>
      </div>
      <div class="card-content">
        <span class="value">{{ formatPercent(marketData.vol_mkt_cap_24h) }}</span>
      </div>
    </div>

    <!-- High/Low Card -->
    <div v-if="!compact" class="data-card">
      <div class="card-header">
        <span class="card-title">24h Range</span>
        <i class="fas fa-arrows-alt-v card-icon"></i>
      </div>
      <div class="card-content">
        <div class="range">
          <span class="high">${{ formatPrice(marketData.high_24h) }}</span>
          <span class="low">${{ formatPrice(marketData.low_24h) }}</span>
        </div>
      </div>
    </div>

    <!-- Supply Card -->
    <div v-if="!compact" class="data-card supply-card">
      <div class="card-header">
        <span class="card-title">Supply</span>
        <i class="fas fa-database card-icon"></i>
      </div>
      <div class="card-content">
        <div class="supply-info">
          <div class="supply-row">
            <span class="label">Circulating:</span>
            <span class="value">{{ formatNumber(marketData.supply.circulating) }}</span>
          </div>
          <div v-if="marketData.supply.total !== marketData.supply.circulating" class="supply-row">
            <span class="label">Total:</span>
            <span class="value">{{ formatNumber(marketData.supply.total) }}</span>
          </div>
          <div v-if="marketData.supply.max > 0" class="supply-row">
            <span class="label">Max:</span>
            <span class="value">{{ formatNumber(marketData.supply.max) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
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
  }
});

// Store
const marketStore = useMarketPreviewStore();

// Computed
const marketData = computed(() => {
  return marketStore.marketData[props.symbol] || getDefaultMarketData();
});

// Default market data
const getDefaultMarketData = () => ({
  symbol: props.symbol,
  price: 0,
  change_24h: 0,
  change_percent_24h: 0,
  market_cap: 0,
  volume_24h: 0,
  fdv: 0,
  vol_mkt_cap_24h: 0,
  high_24h: 0,
  low_24h: 0,
  supply: {
    circulating: 0,
    total: 0,
    max: 0
  }
});

// Formatting functions
const formatPrice = (price) => {
  if (price === 0) return '0.00';
  
  // Determine precision based on price magnitude
  if (price >= 1000) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  } else if (price >= 1) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
  } else {
    // For small prices, show more precision
    return price.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 8 });
  }
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
</script>

<style scoped>
.market-data-cards {
  @apply grid gap-3;
}

.market-data-cards.compact {
  @apply grid-cols-2 md:grid-cols-4;
}

.market-data-cards:not(.compact) {
  @apply grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4;
}

.data-card {
  @apply bg-white/5 border border-white/10 rounded-lg p-4;
  @apply transition-all duration-200 hover:bg-white/10 hover:border-white/20;
}

.price-card {
  @apply bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20;
}

.supply-card {
  @apply md:col-span-2 lg:col-span-1;
}

.card-header {
  @apply flex items-center justify-between mb-2;
}

.card-title {
  @apply text-sm font-medium text-white/80;
}

.card-subtitle {
  @apply text-xs text-white/60;
}

.card-icon {
  @apply text-xs text-white/40;
}

.card-content {
  @apply space-y-1;
}

.price-display {
  @apply flex items-center gap-2;
}

.price {
  @apply text-xl font-bold text-white;
}

.change {
  @apply flex items-center gap-1 text-sm font-medium;
}

.change.positive {
  @apply text-green-400;
}

.change.negative {
  @apply text-red-400;
}

.price-details {
  @apply flex items-center gap-2 text-xs text-white/60;
}

.change-amount {
  @apply text-white/80;
}

.value {
  @apply text-lg font-semibold text-white;
}

.range {
  @apply flex items-center justify-between text-sm;
}

.high {
  @apply text-green-400 font-medium;
}

.low {
  @apply text-red-400 font-medium;
}

.supply-info {
  @apply space-y-1;
}

.supply-row {
  @apply flex items-center justify-between text-sm;
}

.supply-row .label {
  @apply text-white/60;
}

.supply-row .value {
  @apply text-white font-medium;
}

/* Compact mode styles */
.market-data-cards.compact .data-card {
  @apply p-3;
}

.market-data-cards.compact .price {
  @apply text-lg;
}

.market-data-cards.compact .value {
  @apply text-sm;
}

.market-data-cards.compact .card-title {
  @apply text-xs;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .market-data-cards:not(.compact) {
    @apply grid-cols-1;
  }
  
  .market-data-cards.compact {
    @apply grid-cols-1 md:grid-cols-2;
  }
}

/* Loading state */
.data-card.loading {
  @apply animate-pulse;
}

.data-card.loading .value,
.data-card.loading .price {
  @apply bg-white/20 rounded;
  @apply text-transparent;
}
</style>
