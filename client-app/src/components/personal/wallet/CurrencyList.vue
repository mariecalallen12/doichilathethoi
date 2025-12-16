<template>
  <div class="space-y-4">
    <!-- Search and Filter -->
    <div class="glass-panel rounded-lg p-4">
      <div class="flex flex-col md:flex-row space-y-3 md:space-y-0 md:space-x-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Tìm kiếm theo tên hoặc ký hiệu..."
            class="w-full px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:border-purple-500/50 focus:outline-none"
          />
        </div>
        <select
          v-model="balanceFilter"
          class="px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        >
          <option value="all">Tất cả</option>
          <option value="zero">Số dư = 0</option>
          <option value="under100">Dưới $100</option>
          <option value="over1000">Trên $1,000</option>
          <option value="positive">Có số dư</option>
        </select>
        <select
          v-model="sortBy"
          class="px-4 py-2 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white focus:border-purple-500/50 focus:outline-none"
        >
          <option value="alphabetical-asc">A-Z</option>
          <option value="alphabetical-desc">Z-A</option>
          <option value="balance-desc">Số dư cao → thấp</option>
          <option value="balance-asc">Số dư thấp → cao</option>
        </select>
      </div>
    </div>

    <!-- Currency Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <CurrencyCard
        v-for="currency in filteredAndSortedCurrencies"
        :key="currency.currency"
        :currency="currency.currency"
        :total-balance="currency.totalBalance"
        :available-balance="currency.availableBalance"
        :locked-balance="currency.lockedBalance"
        :pending-balance="currency.pendingBalance"
        :change24h="currency.change24h"
      />
    </div>

    <div v-if="filteredAndSortedCurrencies.length === 0" class="text-center py-12 text-purple-300">
      <i class="fas fa-search text-4xl mb-2"></i>
      <p>Không tìm thấy kết quả</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAccountStore } from '../../../stores/account';
import CurrencyCard from '../shared/CurrencyCard.vue';

const accountStore = useAccountStore();
const searchQuery = ref('');
const balanceFilter = ref('all');
const sortBy = ref('alphabetical-asc');

const currencies = computed(() => {
  const list = [];
  
  if (accountStore.currencies?.crypto) {
    Object.entries(accountStore.currencies.crypto).forEach(([currency, data]) => {
      // Normalize currency code
      const normalizedCurrency = (currency || '').trim().toUpperCase();
      if (!normalizedCurrency) return; // Skip invalid currencies
      
      list.push({
        currency: normalizedCurrency,
        totalBalance: data.balance || 0,
        availableBalance: data.balance || 0,
        lockedBalance: 0,
        pendingBalance: 0,
        change24h: null,
      });
    });
  }
  
  if (accountStore.currencies?.fiat) {
    Object.entries(accountStore.currencies.fiat).forEach(([currency, data]) => {
      // Normalize currency code
      const normalizedCurrency = (currency || '').trim().toUpperCase();
      if (!normalizedCurrency) return; // Skip invalid currencies
      
      list.push({
        currency: normalizedCurrency,
        totalBalance: data.balance || 0,
        availableBalance: data.balance || 0,
        lockedBalance: 0,
        pendingBalance: 0,
        change24h: null,
      });
    });
  }
  
  return list;
});

const filteredAndSortedCurrencies = computed(() => {
  let filtered = currencies.value;

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(c => 
      c.currency.toLowerCase().includes(query)
    );
  }

  // Balance filter
  if (balanceFilter.value === 'zero') {
    filtered = filtered.filter(c => c.totalBalance === 0);
  } else if (balanceFilter.value === 'under100') {
    filtered = filtered.filter(c => c.totalBalance < 100);
  } else if (balanceFilter.value === 'over1000') {
    filtered = filtered.filter(c => c.totalBalance > 1000);
  } else if (balanceFilter.value === 'positive') {
    filtered = filtered.filter(c => c.totalBalance > 0);
  }

  // Sort
  if (sortBy.value === 'alphabetical-asc') {
    filtered.sort((a, b) => a.currency.localeCompare(b.currency));
  } else if (sortBy.value === 'alphabetical-desc') {
    filtered.sort((a, b) => b.currency.localeCompare(a.currency));
  } else if (sortBy.value === 'balance-desc') {
    filtered.sort((a, b) => b.totalBalance - a.totalBalance);
  } else if (sortBy.value === 'balance-asc') {
    filtered.sort((a, b) => a.totalBalance - b.totalBalance);
  }

  return filtered;
});
</script>

