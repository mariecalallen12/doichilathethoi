<template>
  <section class="mb-8">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Trading Volume -->
      <div class="market-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-purple-500/20 rounded-lg">
            <i class="fas fa-chart-line text-purple-400 text-2xl"></i>
          </div>
          <div class="text-green-400 text-sm font-semibold">
            <i class="fas fa-arrow-up mr-1"></i>
            +12.5%
          </div>
        </div>
        <h3 class="text-gray-400 text-sm mb-1">Tổng khối lượng giao dịch</h3>
        <p class="text-white text-2xl font-bold">{{ formatVolume(stats.totalVolume) }}</p>
        <p class="text-gray-500 text-xs mt-2">24h volume</p>
      </div>

      <!-- Active Assets -->
      <div class="market-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-blue-500/20 rounded-lg">
            <i class="fas fa-coins text-blue-400 text-2xl"></i>
          </div>
          <div class="text-gray-400 text-sm font-semibold">
            {{ stats.totalAssets }} assets
          </div>
        </div>
        <h3 class="text-gray-400 text-sm mb-1">Tài sản đang hoạt động</h3>
        <p class="text-white text-2xl font-bold">{{ stats.totalAssets }}</p>
        <p class="text-gray-500 text-xs mt-2">Tổng số tài sản</p>
      </div>

      <!-- Markets Up -->
      <div class="market-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-green-500/20 rounded-lg">
            <i class="fas fa-arrow-trend-up text-green-400 text-2xl"></i>
          </div>
          <div class="text-green-400 text-sm font-semibold">
            {{ upPercent }}%
          </div>
        </div>
        <h3 class="text-gray-400 text-sm mb-1">Thị trường tăng</h3>
        <p class="text-white text-2xl font-bold">{{ stats.upMarkets }}</p>
        <p class="text-gray-500 text-xs mt-2">Tài sản đang tăng giá</p>
      </div>

      <!-- Markets Down -->
      <div class="market-card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-red-500/20 rounded-lg">
            <i class="fas fa-arrow-trend-down text-red-400 text-2xl"></i>
          </div>
          <div class="text-red-400 text-sm font-semibold">
            {{ downPercent }}%
          </div>
        </div>
        <h3 class="text-gray-400 text-sm mb-1">Thị trường giảm</h3>
        <p class="text-white text-2xl font-bold">{{ stats.downMarkets }}</p>
        <p class="text-gray-500 text-xs mt-2">Tài sản đang giảm giá</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useMarketStore } from '../../stores/market';
import { formatVolume } from '../../utils/marketFormatters';

const marketStore = useMarketStore();
const stats = computed(() => marketStore.marketStats);

const upPercent = computed(() => {
  if (stats.value.totalAssets === 0) return 0;
  return ((stats.value.upMarkets / stats.value.totalAssets) * 100).toFixed(1);
});

const downPercent = computed(() => {
  if (stats.value.totalAssets === 0) return 0;
  return ((stats.value.downMarkets / stats.value.totalAssets) * 100).toFixed(1);
});
</script>

