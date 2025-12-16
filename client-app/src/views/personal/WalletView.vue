<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-2">Ví Điện Tử</h1>
      <p class="text-purple-300">Quản lý số dư đa tiền tệ</p>
    </div>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Currency List -->
      <div class="lg:col-span-2">
        <CurrencyList />
      </div>

      <!-- Portfolio Analytics -->
      <div class="lg:col-span-1">
        <PortfolioAnalytics />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAccountStore } from '../../stores/account';
import CurrencyList from '../../components/personal/wallet/CurrencyList.vue';
import PortfolioAnalytics from '../../components/personal/wallet/PortfolioAnalytics.vue';

const accountStore = useAccountStore();

onMounted(async () => {
  await accountStore.fetchBalance();
});
</script>

