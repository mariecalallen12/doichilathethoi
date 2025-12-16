<template>
  <section class="mb-8">
    <div class="market-card overflow-hidden">
      <div class="p-6 border-b border-purple-500/20">
        <h2 class="text-xl font-bold text-white">Bảng giá Real-time</h2>
      </div>
      
      <div class="overflow-x-auto market-scrollbar">
        <table class="w-full min-w-[800px]">
          <thead class="bg-purple-500/10">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Tài sản</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Giá hiện tại</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Thay đổi 24h</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Volume</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">High</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Low</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-purple-500/10">
            <tr
              v-for="instrument in filteredInstruments"
              :key="instrument.symbol"
              @click="selectInstrument(instrument)"
              class="price-table-row"
              :class="{ 'bg-purple-500/10': selectedSymbol === instrument.symbol }"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-purple-500/20 to-indigo-500/20 rounded-lg flex items-center justify-center mr-3">
                    <i :class="getAssetIcon(instrument.type)" class="text-purple-400"></i>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-white">{{ instrument.symbol }}</div>
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
    crypto: 'Cryptocurrency',
    commodity: 'Hàng hóa',
    index: 'Chỉ số',
  };
  return names[type] || 'Khác';
};

const getDecimals = (price) => {
  if (price >= 1000) return 2;
  if (price >= 100) return 2;
  if (price >= 10) return 3;
  if (price >= 1) return 4;
  return 5;
};
</script>

