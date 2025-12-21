<template>
  <section class="mb-8">
    <div class="market-card overflow-hidden">
      <div class="p-6 border-b border-purple-500/20">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-bold text-white">Bảng giá Real-time</h2>
          <RealTimeIndicator 
            :isActive="!marketStore.isLoadingInstruments" 
            :updateInterval="5000"
            :showTimer="true"
          />
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="marketStore.isLoadingInstruments && filteredInstruments.length === 0" class="p-12 text-center">
        <i class="fas fa-spinner fa-spin text-purple-400 text-4xl mb-4"></i>
        <p class="text-gray-400 text-lg">Đang tải dữ liệu thị trường...</p>
        <p class="text-gray-500 text-sm mt-2">Kết nối với backend API...</p>
      </div>

      <!-- Price Table -->
      <div v-else class="overflow-x-auto market-scrollbar">
        <table class="w-full min-w-[800px]">
          <thead class="bg-purple-500/10">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Tài sản</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Giá hiện tại</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Thay đổi 24h</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Volume</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">High</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Low</th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Nguồn</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-purple-500/10">
            <tr
              v-for="instrument in filteredInstruments"
              :key="instrument.symbol"
              @click="selectInstrument(instrument)"
              class="price-table-row transition-all duration-200"
              :class="{ 
                'bg-purple-500/10': selectedSymbol === instrument.symbol,
                'price-updated': isPriceUpdated(instrument.symbol)
              }"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-lg flex items-center justify-center mr-3">
                    <i :class="getAssetIcon(instrument.type)" class="text-purple-400"></i>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-white">{{ instrument.displayName || instrument.symbol }}</div>
                    <div class="text-xs text-gray-400">{{ getAssetName(instrument.type) }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="text-sm font-medium text-white" :class="getPriceChangeColor(instrument.changePercent)">
                  {{ formatPrice(instrument.price, getDecimals(instrument.price)) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end">
                  <span 
                    class="text-sm font-semibold px-2 py-1 rounded"
                    :class="[
                      getPriceChangeColor(instrument.changePercent),
                      getPriceChangeBgColor(instrument.changePercent)
                    ]"
                  >
                    {{ formatPercentChange(instrument.changePercent) }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">
                {{ formatVolume(instrument.volume || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-green-400">
                {{ formatPrice(instrument.high || instrument.price, getDecimals(instrument.price)) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-red-400">
                {{ formatPrice(instrument.low || instrument.price, getDecimals(instrument.price)) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span 
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="getSourceBadgeClass(instrument.source)"
                  :title="getSourceTooltip(instrument.source)"
                >
                  <i :class="getSourceIcon(instrument.source)" class="mr-1 text-xs"></i>
                  {{ getSourceLabel(instrument.source) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useMarketStore } from '../../stores/market';
import { formatPrice, formatPercentChange, formatVolume, getPriceChangeColor, getPriceChangeBgColor } from '../../utils/marketFormatters';
import RealTimeIndicator from '../shared/RealTimeIndicator.vue';

const marketStore = useMarketStore();
const selectedSymbol = ref(null);

const filteredInstruments = computed(() => marketStore.filteredAndSortedInstruments);

const selectInstrument = (instrument) => {
  selectedSymbol.value = instrument.symbol;
  marketStore.selectInstrument(instrument);
};

const getAssetIcon = (type) => {
  const icons = {
    forex: 'fas fa-exchange-alt',
    crypto: 'fab fa-bitcoin',
    commodity: 'fas fa-gem',
    index: 'fas fa-chart-bar',
  };
  return icons[type] || 'fas fa-coins';
};

const getAssetName = (type) => {
  const names = {
    forex: 'Forex',
    crypto: 'Crypto',
    commodity: 'Hàng hóa',
    index: 'Chỉ số',
  };
  return names[type] || 'Unknown';
};

const getDecimals = (price) => {
  if (price >= 1000) return 2;
  if (price >= 1) return 4;
  return 8;
};

// Data source helpers
const updatedSymbols = ref(new Set());

const isPriceUpdated = (symbol) => {
  return updatedSymbols.value.has(symbol);
};

const getSourceIcon = (source) => {
  const icons = {
    'binance': 'fas fa-exchange-alt',
    'twelvedata': 'fas fa-globe',
    'self-calculated': 'fas fa-database',
    'api': 'fas fa-cloud',
    'fallback-no-change': 'fas fa-exclamation-triangle'
  };
  return icons[source] || 'fas fa-question-circle';
};

const getSourceLabel = (source) => {
  const labels = {
    'binance': 'Binance',
    'twelvedata': 'Live',
    'self-calculated': 'Calc',
    'api': 'API',
    'fallback-no-change': 'Static'
  };
  return labels[source] || 'Unknown';
};

const getSourceBadgeClass = (source) => {
  const classes = {
    'binance': 'bg-green-500/20 text-green-400',
    'twelvedata': 'bg-blue-500/20 text-blue-400',
    'self-calculated': 'bg-purple-500/20 text-purple-400',
    'api': 'bg-cyan-500/20 text-cyan-400',
    'fallback-no-change': 'bg-yellow-500/20 text-yellow-400'
  };
  return classes[source] || 'bg-gray-500/20 text-gray-400';
};

const getSourceTooltip = (source) => {
  const tooltips = {
    'binance': 'Dữ liệu trực tiếp từ Binance',
    'twelvedata': 'Dữ liệu real-time từ Twelve Data API',
    'self-calculated': 'Tính toán từ dữ liệu lịch sử',
    'api': 'Dữ liệu từ API backend',
    'fallback-no-change': 'Dữ liệu tĩnh (API không khả dụng)'
  };
  return tooltips[source] || 'Nguồn không xác định';
};

// Watch for price updates
import { watch } from 'vue';
watch(() => marketStore.priceData, (newData, oldData) => {
  if (!oldData) return;
  
  newData.forEach((newPrice, symbol) => {
    const oldPrice = oldData.get(symbol);
    if (oldPrice && newPrice.price !== oldPrice.price) {
      updatedSymbols.value.add(symbol);
      setTimeout(() => {
        updatedSymbols.value.delete(symbol);
      }, 1000);
    }
  });
}, { deep: true });
</script>


<style scoped>
.price-table-row {
  cursor: pointer;
  transition: all 0.2s ease;
}

.price-table-row:hover {
  background-color: rgba(139, 92, 246, 0.1) !important;
  transform: translateX(2px);
}

.price-updated {
  animation: pulse-green 1s ease-in-out;
}

@keyframes pulse-green {
  0%, 100% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(34, 197, 94, 0.15);
  }
}

.market-scrollbar::-webkit-scrollbar {
  height: 8px;
}

.market-scrollbar::-webkit-scrollbar-track {
  background: rgba(139, 92, 246, 0.1);
  border-radius: 4px;
}

.market-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 4px;
}

.market-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.7);
}
</style>
