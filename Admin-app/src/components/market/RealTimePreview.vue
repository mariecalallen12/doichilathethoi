<template>
  <div class="real-time-preview">
    <h3 class="preview-title">
      <i class="fas fa-eye text-purple-400"></i>
      Real-time Preview
    </h3>

    <div class="preview-controls">
      <label class="toggle-label">
        <input 
          type="checkbox" 
          v-model="autoRefresh"
          class="checkbox"
        />
        <span>Auto-refresh ({{ refreshInterval }}s)</span>
      </label>

      <button @click="refreshPreview" class="btn-refresh" :disabled="loading">
        <i class="fas fa-sync" :class="{ 'fa-spin': loading }"></i>
        Refresh Now
      </button>
    </div>

    <div v-if="previewData.length === 0" class="empty-state">
      <i class="fas fa-chart-line text-gray-500 text-4xl mb-3"></i>
      <p class="text-gray-400">No preview data available</p>
      <button @click="refreshPreview" class="btn-primary mt-3">
        Load Preview
      </button>
    </div>

    <div v-else class="preview-grid">
      <div 
        v-for="item in previewData" 
        :key="item.symbol"
        class="preview-card"
      >
        <!-- Symbol Header -->
        <div class="preview-header">
          <div class="flex items-center gap-2">
            <img 
              :src="getCryptoIcon(item.symbol)" 
              :alt="item.symbol"
              class="crypto-icon"
              @error="handleIconError"
            />
            <span class="symbol-name">{{ item.symbol }}</span>
          </div>
          <span 
            v-if="item.is_modified"
            class="modified-badge"
          >
            MODIFIED
          </span>
        </div>

        <!-- Price Comparison -->
        <div class="comparison-section">
          <div class="comparison-row">
            <div class="label">Original Price:</div>
            <div class="value original">
              ${{ formatPrice(item.original_price) }}
            </div>
          </div>

          <div class="comparison-arrow">
            <i class="fas fa-arrow-down" :class="getArrowClass(item)"></i>
          </div>

          <div class="comparison-row modified-row">
            <div class="label">Modified Price:</div>
            <div class="value modified">
              ${{ formatPrice(item.modified_price) }}
            </div>
          </div>

          <div class="difference" :class="getDifferenceClass(item)">
            {{ getDifference(item) }}
          </div>
        </div>

        <!-- Signal Comparison -->
        <div class="comparison-section">
          <div class="signal-comparison">
            <div class="signal-item">
              <span class="signal-label">Original:</span>
              <span class="signal-badge" :class="getSignalClass(item.original_signal)">
                {{ item.original_signal }}
              </span>
            </div>
            <i class="fas fa-arrow-right text-gray-500"></i>
            <div class="signal-item">
              <span class="signal-label">Modified:</span>
              <span class="signal-badge" :class="getSignalClass(item.modified_signal)">
                {{ item.modified_signal }}
              </span>
            </div>
          </div>
        </div>

        <!-- Confidence Comparison -->
        <div class="comparison-section">
          <div class="confidence-comparison">
            <div class="confidence-bar-container">
              <div class="confidence-label">Original Confidence</div>
              <div class="confidence-bar">
                <div 
                  class="confidence-fill original"
                  :style="{ width: item.original_confidence + '%' }"
                >
                  {{ item.original_confidence }}%
                </div>
              </div>
            </div>

            <div class="confidence-bar-container">
              <div class="confidence-label">Modified Confidence</div>
              <div class="confidence-bar">
                <div 
                  class="confidence-fill modified"
                  :style="{ width: item.modified_confidence + '%' }"
                >
                  {{ item.modified_confidence }}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Info -->
        <div class="additional-info">
          <div class="info-item">
            <i class="fas fa-chart-line"></i>
            <span>24h Change: {{ item.change_24h }}%</span>
          </div>
          <div class="info-item">
            <i class="fas fa-coins"></i>
            <span>Volume: ${{ formatVolume(item.volume) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div v-if="previewData.length > 0" class="summary-stats">
      <div class="stat-card">
        <div class="stat-label">Total Symbols</div>
        <div class="stat-value">{{ previewData.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Modified</div>
        <div class="stat-value modified">{{ modifiedCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Price Impact</div>
        <div class="stat-value" :class="avgImpactClass">
          {{ avgPriceImpact }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Confidence Boost</div>
        <div class="stat-value positive">
          +{{ avgConfidenceBoost }}%
        </div>
      </div>
    </div>

    <!-- Last Updated -->
    <div v-if="lastUpdated" class="last-updated">
      <i class="fas fa-clock"></i>
      Last updated: {{ formatTime(lastUpdated) }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  apiBaseUrl: {
    type: String,
    default: 'http://localhost:8001'
  },
  symbols: {
    type: Array,
    default: () => ['BTC', 'ETH', 'XRP', 'SOL', 'ADA']
  }
});

const emit = defineEmits(['update']);

// State
const loading = ref(false);
const autoRefresh = ref(true);
const refreshInterval = ref(5);
const previewData = ref([]);
const lastUpdated = ref(null);
let refreshTimer = null;

// Computed
const modifiedCount = computed(() => {
  return previewData.value.filter(item => item.is_modified).length;
});

const avgPriceImpact = computed(() => {
  if (previewData.value.length === 0) return '0.00';
  const total = previewData.value.reduce((sum, item) => {
    const impact = ((item.modified_price - item.original_price) / item.original_price) * 100;
    return sum + impact;
  }, 0);
  return (total / previewData.value.length).toFixed(2);
});

const avgConfidenceBoost = computed(() => {
  if (previewData.value.length === 0) return '0.00';
  const total = previewData.value.reduce((sum, item) => {
    return sum + (item.modified_confidence - item.original_confidence);
  }, 0);
  return (total / previewData.value.length).toFixed(2);
});

const avgImpactClass = computed(() => {
  const impact = parseFloat(avgPriceImpact.value);
  if (impact > 0) return 'positive';
  if (impact < 0) return 'negative';
  return '';
});

// Methods
const refreshPreview = async () => {
  loading.value = true;
  try {
    // Fetch original market data
    const marketResponse = await axios.get(`${props.apiBaseUrl}/market/overview`);
    const originalData = marketResponse.data.data || [];

    // Fetch active customizations
    const customResponse = await axios.get(`${props.apiBaseUrl}/admin/market-control/active`);
    const customizations = customResponse.data;

    // Build preview data
    previewData.value = props.symbols.map(symbol => {
      const original = originalData.find(d => d.symbol === symbol) || {};
      
      // Simulate customization application
      const modified = applyCustomizations(original, customizations);

      return {
        symbol,
        original_price: original.current_price || 0,
        modified_price: modified.price || original.current_price || 0,
        original_signal: original.signal || 'NEUTRAL',
        modified_signal: modified.signal || original.signal || 'NEUTRAL',
        original_confidence: original.confidence || 50,
        modified_confidence: modified.confidence || original.confidence || 50,
        change_24h: original.change_24h || 0,
        volume: original.volume_24h || 0,
        is_modified: modified.is_modified || false
      };
    });

    lastUpdated.value = new Date();
    emit('update', previewData.value);
  } catch (error) {
    console.error('Error fetching preview data:', error);
  } finally {
    loading.value = false;
  }
};

const applyCustomizations = (original, customizations) => {
  if (!customizations.enabled) {
    return { ...original, is_modified: false };
  }

  let modified = { ...original };
  let is_modified = false;

  // Apply price adjustments
  if (customizations.manual_overrides?.prices?.[original.symbol]) {
    modified.price = parseFloat(customizations.manual_overrides.prices[original.symbol].replace(/[$,]/g, ''));
    is_modified = true;
  }

  // Apply signal overrides
  if (customizations.manual_overrides?.signals?.[original.symbol]) {
    modified.signal = customizations.manual_overrides.signals[original.symbol];
    is_modified = true;
  }

  // Apply confidence boosts
  if (customizations.manual_overrides?.confidence_boosts?.[original.symbol]) {
    const boost = parseFloat(customizations.manual_overrides.confidence_boosts[original.symbol].replace(/[+%]/g, ''));
    modified.confidence = Math.min(100, (original.confidence || 50) + boost);
    is_modified = true;
  }

  modified.is_modified = is_modified;
  return modified;
};

const getCryptoIcon = (symbol) => {
  return `https://cryptoicons.org/api/icon/${symbol.toLowerCase()}/32`;
};

const handleIconError = (e) => {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><circle cx="16" cy="16" r="15" fill="%236366f1"/><text x="16" y="22" text-anchor="middle" fill="white" font-size="16">₿</text></svg>';
};

const formatPrice = (price) => {
  if (!price) return '0.00';
  return parseFloat(price).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

const formatVolume = (volume) => {
  if (!volume) return '0';
  if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
  if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
  if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
  return volume.toFixed(0);
};

const getDifference = (item) => {
  const diff = ((item.modified_price - item.original_price) / item.original_price) * 100;
  const sign = diff >= 0 ? '+' : '';
  return `${sign}${diff.toFixed(2)}%`;
};

const getDifferenceClass = (item) => {
  const diff = item.modified_price - item.original_price;
  if (diff > 0) return 'positive';
  if (diff < 0) return 'negative';
  return 'neutral';
};

const getArrowClass = (item) => {
  const diff = item.modified_price - item.original_price;
  if (diff > 0) return 'text-green-400';
  if (diff < 0) return 'text-red-400';
  return 'text-gray-400';
};

const getSignalClass = (signal) => {
  const classes = {
    'STRONG_BUY': 'signal-strong-buy',
    'BUY': 'signal-buy',
    'UP': 'signal-up',
    'NEUTRAL': 'signal-neutral',
    'DOWN': 'signal-down',
    'SELL': 'signal-sell',
    'STRONG_SELL': 'signal-strong-sell'
  };
  return classes[signal] || 'signal-neutral';
};

const formatTime = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
  if (autoRefresh.value) {
    refreshTimer = setInterval(refreshPreview, refreshInterval.value * 1000);
  }
};

// Watchers
watch(autoRefresh, (newValue) => {
  if (newValue) {
    startAutoRefresh();
  } else if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});

// Lifecycle
onMounted(() => {
  refreshPreview();
  startAutoRefresh();
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});
</script>

<style scoped>
.real-time-preview {
  margin-top: 1.5rem;
}

.preview-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #d1d5db;
  cursor: pointer;
}

.checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.btn-refresh {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6366f1;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(99, 102, 241, 0.3);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.preview-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.3s;
}

.preview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.crypto-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.symbol-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.modified-badge {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.comparison-section {
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
}

.comparison-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.label {
  color: #9ca3af;
  font-size: 0.875rem;
}

.value {
  font-size: 1.125rem;
  font-weight: 700;
}

.value.original {
  color: #94a3b8;
}

.value.modified {
  color: #a78bfa;
}

.comparison-arrow {
  text-align: center;
  margin: 0.5rem 0;
  font-size: 1.5rem;
}

.difference {
  text-align: center;
  font-size: 1rem;
  font-weight: 700;
  margin-top: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.difference.positive {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.difference.negative {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.difference.neutral {
  color: #6b7280;
}

.signal-comparison {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.signal-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.signal-label {
  color: #9ca3af;
  font-size: 0.75rem;
}

.signal-badge {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-align: center;
}

.signal-strong-buy {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border: 1px solid #22c55e;
}

.signal-buy {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid #4ade80;
}

.signal-up {
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
  border: 1px solid #86efac;
}

.signal-neutral {
  background: rgba(107, 114, 128, 0.1);
  color: #9ca3af;
  border: 1px solid #6b7280;
}

.signal-down {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  border: 1px solid #fca5a5;
}

.signal-sell {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid #f87171;
}

.signal-strong-sell {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid #ef4444;
}

.confidence-comparison {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.confidence-bar-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.confidence-label {
  color: #9ca3af;
  font-size: 0.75rem;
}

.confidence-bar {
  height: 24px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  overflow: hidden;
  position: relative;
}

.confidence-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  transition: width 0.3s ease;
}

.confidence-fill.original {
  background: linear-gradient(90deg, #64748b 0%, #475569 100%);
}

.confidence-fill.modified {
  background: linear-gradient(90deg, #8b5cf6 0%, #6366f1 100%);
}

.additional-info {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #9ca3af;
  font-size: 0.875rem;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.stat-label {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
}

.stat-value.modified {
  color: #ef4444;
}

.stat-value.positive {
  color: #22c55e;
}

.stat-value.negative {
  color: #ef4444;
}

.last-updated {
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

@media (max-width: 768px) {
  .preview-grid {
    grid-template-columns: 1fr;
  }

  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .signal-comparison {
    flex-direction: column;
  }
}
</style>
