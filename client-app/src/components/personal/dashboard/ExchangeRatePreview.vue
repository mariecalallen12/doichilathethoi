<template>
  <div class="glass-panel rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-white flex items-center">
        <i class="fas fa-exchange-alt mr-2 text-purple-400"></i>
        Tỷ Giá Hôm Nay
      </h3>
      <router-link
        to="/personal/rates"
        class="text-purple-300 hover:text-white text-sm transition-colors"
      >
        Xem chi tiết <i class="fas fa-arrow-right ml-1"></i>
      </router-link>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 bg-slate-800/50 rounded-lg animate-pulse"></div>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="rate in rates"
        :key="rate.pair"
        class="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg"
      >
        <div>
          <div class="text-white font-medium mb-1">{{ rate.pair }}</div>
          <div class="text-purple-300 text-xs">{{ rate.label }}</div>
        </div>
        <div class="text-right">
          <div class="font-orbitron text-xl font-bold text-white mb-1">
            {{ formatRate(rate.rate) }}
          </div>
          <div
            :class="[
              'text-sm font-medium',
              rate.change >= 0 ? 'text-green-400' : 'text-red-400'
            ]"
          >
            <i :class="rate.change >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ Math.abs(rate.change).toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4 pt-4 border-t border-purple-500/20 text-purple-300 text-xs text-center">
      Cập nhật mỗi phút • Nguồn: Binance
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { formatNumber } from '../../../services/utils/formatters';
import { useExchangeRatesStore } from '../../../stores/exchangeRates';
import { clientApi } from '../../../services/api/client';

const exchangeRatesStore = useExchangeRatesStore();

const rates = ref([]);
const loading = ref(false);

const formatRate = (rate) => {
  return `${formatNumber(rate)} VND`;
};

const mapDashboardExchangeRates = (exchangeRates) => {
  if (!exchangeRates || !Array.isArray(exchangeRates)) return [];

  // Ưu tiên các cặp từ USDT sang VND/USD/EUR/GBP/CNY
  const preferredTargets = ['VND', 'USD', 'EUR', 'GBP', 'CNY'];

  const mapped = exchangeRates
    .filter((r) => r.baseAsset === 'USDT' && preferredTargets.includes(r.targetAsset))
    .map((r) => ({
      pair: `USDT → ${r.targetAsset}`,
      label: `Tether to ${r.targetAsset}`,
      rate: r.rate,
      change: r.change24h || 0,
    }));

  return mapped;
};

const loadRates = async () => {
  loading.value = true;
  try {
    // Thử lấy từ dashboard để đảm bảo đồng bộ với view chính
    const dashboard = await clientApi.getDashboard();
    const data = dashboard.data || dashboard;

    const fromDashboard = mapDashboardExchangeRates(data.exchangeRates);
    if (fromDashboard.length > 0) {
      rates.value = fromDashboard;
      return;
    }

    // Nếu dashboard không cung cấp đủ, fallback sang store exchangeRates
    await exchangeRatesStore.fetchRates();
    const usdtToVnd = exchangeRatesStore.getRate('USDT', 'VND');

    rates.value = [
      {
        pair: 'USDT → VND',
        label: 'Tether to Vietnamese Dong',
        rate: usdtToVnd || 24850,
        change: 0,
      },
    ];
  } catch (e) {
    console.error('Failed to load exchange rate preview:', e);
    // Fallback giá trị tĩnh
    rates.value = [
      {
        pair: 'USDT → VND',
        label: 'Tether to Vietnamese Dong',
        rate: 24850,
        change: 0,
      },
    ];
  } finally {
    loading.value = false;
  }
};

// Auto-refresh every minute
let refreshInterval = null;

onMounted(async () => {
  await loadRates();

  refreshInterval = setInterval(() => {
    loadRates().catch((e) => console.error('Auto-refresh rate preview failed:', e));
  }, 60000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>
